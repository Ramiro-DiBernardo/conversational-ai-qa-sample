"""Rule-based QA for debt-collection chatbot / voicebot conversations.

Reads synthetic transcripts, applies compliance and quality checks inspired by the
FDCPA and CFPB Regulation F, audits the vendor's pass/fail scores, and writes:
  - reports/qa_results.csv      one row per finding
  - reports/vendor_audit.csv    vendor score vs. our score, with the reason
  - reports/call_frequency.csv  7-in-7 call frequency check (Reg F)
  - reports/summary.md          human-readable summary

Standard library only. Run:  python src/qa_checks.py
Educational sample: all data is fictional and this is not legal advice.
"""
import csv
import json
import re
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA, OUT = ROOT / "data", ROOT / "reports"
OUT.mkdir(exist_ok=True)

MINI_MIRANDA = re.compile(r"debt collector.*attempt to collect a debt", re.I | re.S)
DEBT_MENTION = re.compile(r"balance|owe|overdue|debt|\$\d", re.I)
IDENTITY_STEP = re.compile(r"confirm (your )?(date of birth|the last 4 digits)", re.I)
THIRD_PARTY = re.compile(r"\b(this is (his|her|their) (sister|brother|wife|husband|mother|father|son|daughter)|not (him|her|them)|wrong number)\b", re.I)

# Situations the bot must recognise even when the customer doesn't use the legal term.
TRIGGERS = {
    "dispute": re.compile(r"not mine|never had (an )?account|already paid|don'?t recognize|identity theft|this is a mistake", re.I),
    "hardship": re.compile(r"lost my job|hospital|barely|can'?t afford|money is (really )?tight|sick|medical bills", re.I),
    "attorney": re.compile(r"attorney|lawyer", re.I),
    "bankruptcy": re.compile(r"bankrupt|chapter (7|13)", re.I),
    "military": re.compile(r"active duty|deployed|military|servicemember", re.I),
    "cease": re.compile(r"stop (contacting|calling)|do not (call|contact|text)|don'?t (call|contact|text) me", re.I),
}
# What a correct bot response looks like after each trigger.
CORRECT_HANDLING = re.compile(r"paus(e|ing) collection|transfer(ring)? you to a specialist|noted that you dispute|hardship options|won'?t contact you|specialist", re.I)
PRESSURE_AFTER_TRIGGER = re.compile(r"pay|payment|when can you", re.I)
THREATS = re.compile(r"arrest|jail|police|sue you today|garnish", re.I)
MONEY = re.compile(r"\$([\d,]+(?:\.\d{2})?)")

SEVERITY = {"critical": 3, "high": 2, "medium": 1}


def money(s):
    return float(s.replace(",", ""))


def check(conv):
    """Return a list of (rule, severity, detail) findings for one conversation."""
    f = []
    turns = conv["turns"]
    if conv.get("silent_call") or not turns:
        return [("silent_call", "medium", "No audio/text captured; needs manual review and a technical ticket.")]

    bot_lines = [(i, t) for i, (who, t) in enumerate(turns) if who == "bot"]
    cust_lines = [(i, t) for i, (who, t) in enumerate(turns) if who == "customer"]

    # 1. Contact hours: 8:00-21:00 consumer local time (FDCPA).
    hh, mm = map(int, conv["local_time"].split(":"))
    if hh < 8 or (hh, mm) >= (21, 0):
        f.append(("contact_hours", "high", f"Contact at {conv['local_time']} local time, outside 8:00-21:00."))

    # 2. Third-party disclosure: debt mentioned to someone who is not the consumer.
    third = next((i for i, t in cust_lines if THIRD_PARTY.search(t)), None)
    if third is not None and any(i > third and DEBT_MENTION.search(t) for i, t in bot_lines):
        f.append(("third_party_disclosure", "critical", "Debt details shared with a third party."))

    # 3. Identity verification must happen before the debt is mentioned.
    first_debt = next((i for i, t in bot_lines if DEBT_MENTION.search(t)), None)
    first_id = next((i for i, t in bot_lines if IDENTITY_STEP.search(t)), None)
    if first_debt is not None and (first_id is None or first_id > first_debt):
        f.append(("identity_before_disclosure", "critical", "Debt mentioned before verifying the consumer's identity."))

    # 4. Mini-Miranda disclosure must be present when the debt is discussed.
    if first_debt is not None and not any(MINI_MIRANDA.search(t) for _, t in bot_lines):
        f.append(("mini_miranda_missing", "high", "Required debt-collector disclosure is missing."))

    # 5. Special situations: detect the trigger, then check the bot's next response.
    for name, rx in TRIGGERS.items():
        for i, t in cust_lines:
            if rx.search(t):
                nxt = next((bt for bi, bt in bot_lines if bi > i), "")
                if not CORRECT_HANDLING.search(nxt) and PRESSURE_AFTER_TRIGGER.search(nxt):
                    sev = "critical" if name in {"dispute", "attorney", "bankruptcy", "cease", "military"} else "high"
                    f.append((f"{name}_not_handled", sev, f'Customer: "{t}" -> Bot kept collecting: "{nxt}"'))
                break

    # 6. False threats / deceptive statements.
    for _, t in bot_lines:
        if THREATS.search(t):
            f.append(("false_threat", "critical", f'Bot used a threat: "{t}"'))

    # 7. Payment plan math must match the account balance.
    if conv.get("plan_amount_total") is not None and abs(conv["plan_amount_total"] - conv["account_balance"]) > 0.01:
        f.append(("payment_amount_mismatch", "high",
                  f"Plan totals ${conv['plan_amount_total']:,.2f} but balance is ${conv['account_balance']:,.2f}."))

    # 8. System of record must be updated after a payment/plan.
    if any(re.search(r"payment .*received|scheduled|plan is confirmed", t, re.I) for _, t in bot_lines) and not conv.get("system_updated"):
        f.append(("system_not_updated", "medium", "Payment confirmed to the customer but the account was not updated."))
    return f


def call_frequency():
    """Reg F presumption: more than 7 call attempts within 7 consecutive days."""
    attempts = defaultdict(list)
    with open(DATA / "call_log.csv", newline="") as fh:
        for r in csv.DictReader(fh):
            attempts[r["account"]].append(date.fromisoformat(r["attempt_date"]))
    rows = []
    for acc, ds in sorted(attempts.items()):
        ds.sort()
        worst = max(sum(1 for d in ds if start <= d < start + timedelta(days=7)) for start in ds)
        rows.append({"account": acc, "max_attempts_in_7_days": worst, "result": "FAIL" if worst > 7 else "PASS"})
    return rows


def main():
    convs = [json.loads(l) for l in open(DATA / "transcripts.jsonl", encoding="utf-8") if l.strip()]
    vendor = {r["conversation_id"]: r for r in csv.DictReader(open(DATA / "vendor_qa_scores.csv", newline=""))}

    findings, audit = [], []
    for c in convs:
        fs = check(c)
        for rule, sev, detail in fs:
            findings.append({"conversation_id": c["id"], "rule": rule, "severity": sev, "detail": detail})
        ours = "FAIL" if any(SEVERITY[s] >= 2 for _, s, _ in fs) else ("REVIEW" if fs else "PASS")
        v = vendor.get(c["id"], {})
        agree = (v.get("vendor_result") == ours) or (ours == "REVIEW" and v.get("vendor_result") == "PASS")
        audit.append({"conversation_id": c["id"], "vendor_result": v.get("vendor_result", ""), "our_result": ours,
                      "agreement": "yes" if agree else "NO - dispute vendor score",
                      "reason": "; ".join(r for r, _, _ in fs) or "no findings"})

    with open(OUT / "qa_results.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["conversation_id", "rule", "severity", "detail"]); w.writeheader(); w.writerows(findings)
    with open(OUT / "vendor_audit.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(audit[0])); w.writeheader(); w.writerows(audit)
    freq = call_frequency()
    with open(OUT / "call_frequency.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(freq[0])); w.writeheader(); w.writerows(freq)

    n = len(convs)
    passed = sum(1 for a in audit if a["our_result"] == "PASS")
    disputes = [a for a in audit if a["agreement"] != "yes"]
    by_rule = defaultdict(int)
    for x in findings:
        by_rule[x["rule"]] += 1
    lines = [
        "# QA summary", "",
        f"- Conversations reviewed: **{n}**",
        f"- Compliance pass rate: **{passed}/{n} ({passed / n:.0%})**",
        f"- Findings: **{len(findings)}** ({sum(1 for x in findings if x['severity'] == 'critical')} critical)",
        f"- Vendor scores disputed: **{len(disputes)}/{n}**",
        f"- Accounts over the 7-in-7 call limit: **{sum(1 for r in freq if r['result'] == 'FAIL')}/{len(freq)}**", "",
        "## Findings by rule", "", "| Rule | Count |", "|---|---|",
        *[f"| `{r}` | {c} |" for r, c in sorted(by_rule.items(), key=lambda kv: -kv[1])], "",
        "## Vendor scores we dispute", "", "| Conversation | Vendor | Ours | Why |", "|---|---|---|---|",
        *[f"| {a['conversation_id']} | {a['vendor_result']} | {a['our_result']} | {a['reason']} |" for a in disputes],
    ]
    (OUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
