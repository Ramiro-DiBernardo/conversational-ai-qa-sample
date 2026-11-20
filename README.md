# Conversational AI QA: Collections Chatbot / Voicebot

A sample project I built to show how I approach quality assurance for conversational AI in a regulated industry (U.S. debt collection). It has two parts:

1. **A manual QA test suite** (Excel): test cases, fail criteria and a transcript scorecard.
2. **An automated QA checker** (Python): reviews bot transcripts against compliance rules and audits a vendor's pass/fail scores.

> All scenarios and data are fictional and created for demonstration. Rule references (FDCPA, CFPB Regulation F) are a study aid, not legal advice.

## Part 1 — Manual test suite

`collections-chatbot-qa-test-cases.xlsx`

| Sheet | Purpose |
|---|---|
| **Summary** | Auto-calculated metrics: executed, passed, failed, critical failures, pass rate |
| **Test Cases** | 18 scenarios with consumer input, expected bot behavior, explicit fail criteria, rule/SOP reference, severity and result |
| **Transcript Scorecard** | Weighted rubric to score a full bot conversation, with an automatic "compliance miss" flag |

**Coverage**

- **Identity & privacy:** right-party verification, third parties answering the call
- **Required disclosures:** debt-collector disclosure, opt-out in electronic messages
- **Compliance red flags:** disputes, cease-contact requests, attorney representation, bankruptcy, deceased consumers
- **No threats / no misleading statements:** consequences questions, invented promises (hallucination checks)
- **Accuracy:** balances, fees and payment promises must match account data
- **Customer experience:** hardship, angry consumers, escalation to a human, Spanish-speaking consumers, contact preferences

## Part 2 — Automated QA checker

`src/qa_checks.py` (Python standard library only) reviews each conversation and checks:

- contact hours (8:00–21:00 consumer local time)
- identity verified **before** the debt is mentioned; no third-party disclosure
- required debt-collector disclosure ("mini-Miranda")
- special situations detected **even when the consumer doesn't use the legal term** ("that's not mine" = dispute), and whether the bot stopped collecting: dispute, hardship, attorney, bankruptcy, active-duty military, cease contact
- false threats, payment-plan math, system of record updated, silent calls
- Regulation F call frequency ("7 calls in 7 days")

It then **audits the vendor's QA scores**, confirming or disputing each pass/fail and recording why.

**Results on the sample data (16 synthetic conversations)**

| Metric | Value |
|---|---|
| Compliance pass rate | 4/16 (25%) |
| Findings | 14 (7 critical) |
| Vendor scores disputed | 8/16 |
| Accounts over the 7-in-7 call limit | 1/3 |

Example of a conversation the vendor marked as **PASS**:

> **C003** — Consumer: *"That's not mine, I never had an account with them."* → Bot: *"Would you like to pay the full amount today or set up a plan?"*
> **Critical: implicit dispute not handled.** The bot should pause collection and record the dispute.

Outputs: [`reports/summary.md`](reports/summary.md), [`reports/qa_results.csv`](reports/qa_results.csv), [`reports/vendor_audit.csv`](reports/vendor_audit.csv), [`reports/call_frequency.csv`](reports/call_frequency.csv). The 15-point review checklist is in [`docs/qa_checklist.md`](docs/qa_checklist.md) and the fix-validation test plan in [`docs/test_plan.csv`](docs/test_plan.csv).

Run it:

```bash
python src/qa_checks.py
```

## Approach

1. Every case has a clear **FAIL if** condition, so two reviewers reach the same verdict.
2. Severity drives priority: a single **Critical** failure (compliance) outweighs several tone issues.
3. Full transcripts are scored with a weighted rubric; missing any compliance criterion is an automatic fail.
4. When my score and the vendor's disagree, I record the exact rule and turn, correct the score and bring unclear cases to calibration.

## Project structure

```
collections-chatbot-qa-test-cases.xlsx   manual test suite and scorecard
data/       synthetic transcripts, vendor QA scores, call log
docs/       review checklist and test plan
src/        automated QA checker
reports/    generated outputs
```

## Next steps

- Compare the keyword rules with an LLM-assisted classifier on a labelled set, keeping humans in the loop for critical cases.
- Add a Power BI dashboard over the QA results (pass rate over time, findings by rule, vendor agreement).

---
Ramiro Di Bernardo · [LinkedIn](https://www.linkedin.com/in/ramiro-di-bernardo) · [GitHub](https://github.com/Ramiro-DiBernardo)
