from retrieval import retrieve_documents


if __name__ == "__main__":

    question = input("Enter your legal question: ")

    results = retrieve_documents(question, top_k=5)

    print()
    print("=" * 70)

    if not results:
        print("NO DOCUMENTS PASSED THE RETRIEVAL FILTER.")
        print()
        print("The query may have relevant results, but they were")
        print("removed because their distance exceeded MAX_DISTANCE.")
        print("=" * 70)

    else:
        for index, result in enumerate(results, start=1):

            print(f"RESULT {index}")
            print(f"Page: {result['page_number']}")
            print(f"Section: {result.get('section')}")
            print(f"Distance: {result['distance']:.4f}")
            print()

            print(result["text"])

            print()
            print("=" * 70)