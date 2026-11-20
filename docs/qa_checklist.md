# QA checklist — debt-collection voicebot / chatbot

Use this checklist for every reviewed conversation, in this order. A conversation **fails** if any *critical* or *high* item fails.

| # | Check | Severity | Based on |
|---|---|---|---|
| 1 | Contact made between **8:00 and 21:00** in the consumer's local time zone | High | FDCPA |
| 2 | **Identity verified** (DOB / last 4 SSN) **before** any mention of the debt | Critical | FDCPA (third-party disclosure) |
| 3 | If someone else answers, **no debt details** are shared | Critical | FDCPA |
| 4 | **Mini-Miranda** disclosure given: "communication from a debt collector… attempt to collect a debt…" | High | FDCPA |
| 5 | **Dispute** detected, even when implicit ("not mine", "already paid") → collection paused, dispute recorded | Critical | FDCPA validation rights |
| 6 | **Attorney** mentioned → stop collecting, route to attorney contact | Critical | FDCPA |
| 7 | **Bankruptcy** mentioned → pause collection (automatic stay), escalate | Critical | Bankruptcy Code |
| 8 | **Active-duty military** mentioned → escalate to SCRA handling | Critical | SCRA |
| 9 | **Cease / do not contact** request → stop contact on that channel, record it | Critical | FDCPA, Reg F |
| 10 | **Hardship** signals → empathetic response, hardship options or human transfer | High | Internal policy / fair treatment |
| 11 | No **threats** (arrest, jail, lawsuit that won't happen) or false statements | Critical | FDCPA |
| 12 | **Payment amounts** and plan totals match the account balance | High | Accuracy |
| 13 | **Account updated** in the system of record after a payment or plan | Medium | Operations |
| 14 | No more than **7 call attempts in 7 days** per debt | High | Reg F |
| 15 | Silent / broken calls flagged for manual review and a technical ticket | Medium | Operations |

## When the vendor's score and ours disagree
1. Re-read the conversation against the SOP and this checklist.
2. Write the exact rule and the exact turn that triggered the decision.
3. Correct the score and bring unclear cases to the weekly calibration.
4. If the bot behaviour is wrong, open a ticket with the transcript, expected behaviour and a test case.
