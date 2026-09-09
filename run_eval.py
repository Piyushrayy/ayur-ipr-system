import json
import requests
import sys
from pathlib import Path

<<<<<<< HEAD
# Adjust endpoint if Dev A is running on a different port or host
API_URL = "http://localhost:8000/api/v1/query"
DATASET_PATH = Path(__file__).resolve().parent.parent / "data" / "ground_truth_testset.json"
=======
API_URL = "http://localhost:8000/api/v1/query"
BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = BASE_DIR / "data" / "ground_truth_testset.json"
REPORT_PATH = BASE_DIR / "evaluation_report.md"
>>>>>>> origin/Kunal-Sharma-35

def run_benchmark():
    if not DATASET_PATH.exists():
        print(f"Error: Dataset not found at {DATASET_PATH}")
        sys.exit(1)

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    total_cases = len(test_cases)
    passed_abstentions = 0
<<<<<<< HEAD
    passed_citations = 0
=======
    passed_retrievals = 0
>>>>>>> origin/Kunal-Sharma-35
    passed_sections = 0
    abstention_cases_count = 0
    applicable_cases_count = 0

<<<<<<< HEAD
    print("=" * 70)
    print(f"STARTING EVALUATION BENCHMARK: {total_cases} CASES")
    print("=" * 70)
=======
    print("=" * 72)
    print(f"STARTING COMPREHENSIVE BENCHMARK: {total_cases} CASES")
    print("=" * 72)
>>>>>>> origin/Kunal-Sharma-35

    for case in test_cases:
        t_id = case["test_id"]
        query = case["question"]
        expected_abstain = case["expected_abstention_behavior"]
        expected_sec = case["expected_section"].lower()

        payload = {
            "query": query,
            "jurisdiction": case["jurisdiction"],
            "language": case["language"]
        }

        try:
<<<<<<< HEAD
            response = requests.post(API_URL, json=payload, timeout=10)
            res_data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"[{t_id}] FAILED TO CONNECT TO API ({e})")
=======
            response = requests.post(API_URL, json=payload, timeout=12)
            res_data = response.json()
        except Exception as e:
            print(f"[{t_id}] FAILED: Backend unreachable ({e})")
>>>>>>> origin/Kunal-Sharma-35
            continue

        actual_abstain = res_data.get("abstain", False)
        citations = res_data.get("citations", [])
<<<<<<< HEAD
        
        # Check abstention accuracy
=======

>>>>>>> origin/Kunal-Sharma-35
        if expected_abstain:
            abstention_cases_count += 1
            if actual_abstain:
                passed_abstentions += 1
<<<<<<< HEAD
                print(f"[{t_id}] PASS: Safely abstained on out-of-scope query.")
            else:
                print(f"[{t_id}] FAIL: Hallucinated an answer instead of abstaining.")
            continue

        applicable_cases_count += 1
        
        # Check if citations exist
        if not citations:
            print(f"[{t_id}] FAIL: No citations returned.")
            continue
        
        passed_citations += 1

        # Check section match in citations
=======
                status = "PASS: Safely abstained on out-of-scope query."
            else:
                status = "FAIL: Hallucinated out-of-scope answer."
            print(f"[{t_id}] {status}")
            continue

        applicable_cases_count += 1
        if not citations:
            print(f"[{t_id}] FAIL: No citations returned.")
            continue

        passed_retrievals += 1
>>>>>>> origin/Kunal-Sharma-35
        found_section = any(
            expected_sec in str(c.get("section", "")).lower() or 
            expected_sec in str(c.get("text", "")).lower() 
            for c in citations
        )

        if found_section:
            passed_sections += 1
            print(f"[{t_id}] PASS: Citation & section '{case['expected_section']}' verified.")
        else:
            print(f"[{t_id}] FAIL: Section mismatch. Expected '{case['expected_section']}'.")

<<<<<<< HEAD
    # Output Summary Metrics for Member F's Presentation
    print("\n" + "=" * 70)
    print("EVALUATION METRIC REPORT (SIH 2026)")
    print("=" * 70)
    if abstention_cases_count > 0:
        abstention_rate = (passed_abstentions / abstention_cases_count) * 100
        print(f"Safe Abstention Accuracy: {abstention_rate:.1f}% ({passed_abstentions}/{abstention_cases_count})")
    
    if applicable_cases_count > 0:
        retrieval_rate = (passed_citations / applicable_cases_count) * 100
        section_rate = (passed_sections / applicable_cases_count) * 100
        print(f"Source Retrieval Rate:    {retrieval_rate:.1f}% ({passed_citations}/{applicable_cases_count})")
        print(f"Section Citation Accuracy: {section_rate:.1f}% ({passed_sections}/{applicable_cases_count})")
    print("=" * 70)
=======
    abstention_rate = (passed_abstentions / abstention_cases_count * 100) if abstention_cases_count else 0
    retrieval_rate = (passed_retrievals / applicable_cases_count * 100) if applicable_cases_count else 0
    section_rate = (passed_sections / applicable_cases_count * 100) if applicable_cases_count else 0

    print("\n" + "=" * 72)
    print("EVALUATION METRIC REPORT (SIH 2026)")
    print("=" * 72)
    print(f"Safe Abstention Accuracy: {abstention_rate:.1f}% ({passed_abstentions}/{abstention_cases_count})")
    print(f"Source Retrieval Rate:    {retrieval_rate:.1f}% ({passed_retrievals}/{applicable_cases_count})")
    print(f"Section Citation Precision: {section_rate:.1f}% ({passed_sections}/{applicable_cases_count})")
    print("=" * 72)

    summary_md = f"""# IP-SAKTI SAHAYAK - Evaluation Benchmark Report

## Target Legal Reliability Metrics
| Metric | Benchmark Result | Target |
| :--- | :--- | :--- |
| **Total Test Scenarios** | **{total_cases} cases** | 35 cases |
| **Safe Abstention Accuracy** | **{abstention_rate:.1f}%** ({passed_abstentions}/{abstention_cases_count}) | > 90% |
| **Source Retrieval Rate** | **{retrieval_rate:.1f}%** ({passed_retrievals}/{applicable_cases_count}) | > 85% |
| **Section Citation Precision** | **{section_rate:.1f}%** ({passed_sections}/{applicable_cases_count}) | > 80% |

### Regimes Tested
- The Patents Act, 1970 (Section 3(p), 3(e), 3(d), 10, 53, 64(1)(p))
- Biological Diversity Act, 2002 / 2023 Amendment (Sections 3, 4, 6, 7, 55)
- Drugs and Cosmetics Act, 1940 & Rules 1945 (First Schedule, Rule 158-B, Schedule T)
- Food Safety and Standards (Ayurveda Aahar) Regulations, 2022
- WIPO GRATK Treaty (2024) Article 3
- Drugs and Magic Remedies (Objectionable Advertisements) Act, 1954
- Protection of Plant Varieties and Farmers' Rights Act, 2001
- Madrid Protocol & Geographical Indications Act
"""
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(summary_md)
>>>>>>> origin/Kunal-Sharma-35

if __name__ == "__main__":
    run_benchmark()