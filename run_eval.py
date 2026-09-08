import json
import requests
import sys
from pathlib import Path

# Adjust endpoint if Dev A is running on a different port or host
API_URL = "http://localhost:8000/api/v1/query"
DATASET_PATH = Path(__file__).resolve().parent.parent / "data" / "ground_truth_testset.json"

def run_benchmark():
    if not DATASET_PATH.exists():
        print(f"Error: Dataset not found at {DATASET_PATH}")
        sys.exit(1)

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    total_cases = len(test_cases)
    passed_abstentions = 0
    passed_citations = 0
    passed_sections = 0
    abstention_cases_count = 0
    applicable_cases_count = 0

    print("=" * 70)
    print(f"STARTING EVALUATION BENCHMARK: {total_cases} CASES")
    print("=" * 70)

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
            response = requests.post(API_URL, json=payload, timeout=10)
            res_data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"[{t_id}] FAILED TO CONNECT TO API ({e})")
            continue

        actual_abstain = res_data.get("abstain", False)
        citations = res_data.get("citations", [])
        
        # Check abstention accuracy
        if expected_abstain:
            abstention_cases_count += 1
            if actual_abstain:
                passed_abstentions += 1
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

if __name__ == "__main__":
    run_benchmark()