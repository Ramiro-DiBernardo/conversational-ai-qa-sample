# Conversational AI QA: Collections Chatbot / Voicebot Test Suite

A sample QA test suite I built to show how I approach quality assurance for conversational AI in a regulated industry (U.S. debt collection).

## What's inside

`collections-chatbot-qa-test-cases.xlsx`

| Sheet | Purpose |
|---|---|
| **Summary** | Auto-calculated metrics: executed, passed, failed, critical failures, pass rate |
| **Test Cases** | 18 scenarios with consumer input, expected bot behavior, explicit fail criteria, rule/SOP reference, severity and result |
| **Transcript Scorecard** | Weighted rubric to score a full bot conversation, with an automatic "compliance miss" flag |

## Coverage

- **Identity & privacy:** right-party verification, third parties answering the call
- **Required disclosures:** debt-collector disclosure, opt-out in electronic messages
- **Compliance red flags:** disputes, cease-contact requests, attorney representation, bankruptcy, deceased consumers
- **No threats / no misleading statements:** consequences questions, invented promises (hallucination checks)
- **Accuracy:** balances, fees and payment promises must match account data
- **Customer experience:** hardship, angry consumers, escalation to a human, Spanish-speaking consumers, contact preferences

## Approach

1. Every case has a clear **FAIL if** condition, so two reviewers reach the same verdict.
2. Severity drives priority: a single **Critical** failure (compliance) outweighs several tone issues.
3. Full transcripts are scored with a weighted rubric; missing any compliance criterion is an automatic fail.

> Scenarios are fictional and created for demonstration. Rule references (FDCPA, CFPB Regulation F) are a study aid, not legal advice.

---
Ramiro Di Bernardo · [LinkedIn](https://www.linkedin.com/in/ramiro-di-bernardo) · [GitHub](https://github.com/Ramiro-DiBernardo)
