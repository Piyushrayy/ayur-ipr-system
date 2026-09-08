from retrieval import retrieve_documents


if __name__ == "__main__":

    jurisdiction = input(
        "Enter jurisdiction (india/international): "
    ).strip().lower()

    question = input(
        "Enter your legal question: "
    )

    results = retrieve_documents(
        question,
        jurisdiction,
        top_k=5
    )

    print()
    print("=" * 70)

    if not results:
        print("No relevant documents found.")
        print("=" * 70)
        exit()

    for index, result in enumerate(
        results,
        start=1
    ):

        print(f"RESULT {index}")
        print(f"Jurisdiction: {result['jurisdiction']}")
        print(f"Source: {result['source_name']}")
        print(f"Page: {result['page_number']}")
        print(f"Section: {result['section']}")
        print(f"Distance: {result['distance']:.4f}")
        print(
            f"Ranking Score: "
            f"{result['ranking_score']:.4f}"
        )
        print(
            f"Section Match: "
            f"{result['section_match']}"
        )
        print()

        print(result["text"])

        print()
        print("=" * 70)