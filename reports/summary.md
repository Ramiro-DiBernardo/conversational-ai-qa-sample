# QA summary

- Conversations reviewed: **16**
- Compliance pass rate: **4/16 (25%)**
- Findings: **14** (7 critical)
- Vendor scores disputed: **8/16**
- Accounts over the 7-in-7 call limit: **1/3**

## Findings by rule

| Rule | Count |
|---|---|
| `mini_miranda_missing` | 2 |
| `third_party_disclosure` | 1 |
| `identity_before_disclosure` | 1 |
| `dispute_not_handled` | 1 |
| `hardship_not_handled` | 1 |
| `attorney_not_handled` | 1 |
| `military_not_handled` | 1 |
| `cease_not_handled` | 1 |
| `contact_hours` | 1 |
| `payment_amount_mismatch` | 1 |
| `false_threat` | 1 |
| `system_not_updated` | 1 |
| `silent_call` | 1 |

## Vendor scores we dispute

| Conversation | Vendor | Ours | Why |
|---|---|---|---|
| C002 | PASS | FAIL | third_party_disclosure; identity_before_disclosure; mini_miranda_missing |
| C003 | PASS | FAIL | dispute_not_handled |
| C004 | PASS | FAIL | hardship_not_handled |
| C007 | PASS | FAIL | military_not_handled |
| C009 | PASS | FAIL | contact_hours |
| C010 | PASS | FAIL | mini_miranda_missing |
| C011 | PASS | FAIL | payment_amount_mismatch |
| C014 | PASS | FAIL | false_threat |
