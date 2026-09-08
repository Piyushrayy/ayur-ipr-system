# IP-SAKTI SAHAYAK - Legal Ground-Truth Evaluation Engine (Member E)

This module contains the legal ground-truth evaluation benchmark and automated verification pipeline for **PS SIH26045** (Ayurvedic IPR & ABS Assistant).

## 1. Golden Evaluation Benchmark (`ground_truth_testset.json`)
Curated set of 15 structured legal test scenarios across statutory regimes:
- **The Patents Act, 1970**: Section 3(p) Traditional Knowledge bar, Section 3(e) Synergistic admixtures, Section 10 Origin disclosure.
- **Biological Diversity Act, 2002 / 2023 Amendment**: Section 3 & Section 6 NBA approvals, Section 7 SBB intimations.
- **Drugs and Cosmetics Act, 1940 & Rules 1945**: First Schedule classical texts, Rule 158-B proof of safety/efficacy.
- **Food Safety and Standards (Ayurveda Aahar) Regulations, 2022**: Regulation 3 non-medicinal classification.
- **International Treaties**: WIPO GRATK Treaty (2024) Article 3 mandatory disclosure.
- **Consumer Protection / Advertising**: Drugs and Magic Remedies Act 1954 Section 3 prohibition.
- **Safe Abstention**: Out-of-scope domain queries to verify the model avoids legal hallucinations.

## 2. Automated Benchmark Runner (`run_eval.py`)
Queries the orchestrator endpoint (`/api/v1/query`) and computes three metrics:
1. **Safe Abstention Accuracy %**: Verifies the system declines out-of-scope queries.
2. **Source Retrieval Rate %**: Verifies relevant legal sources are returned.
3. **Section Citation Precision %**: Verifies citations match exact statutory provisions.

## 3. How to Run
```bash
# Start backend (or local mock server)
python -m uvicorn scripts.mock_server:app --port 8000

# Execute evaluation suite
python scripts/run_eval.py