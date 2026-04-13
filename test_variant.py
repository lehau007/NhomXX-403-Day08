from rag_answer import rag_answer

if __name__ == "__main__":
    # Test queries
    test_queries = [
        "SLA xử lý ticket P1 là bao lâu?",
        "Khách hàng có thể yêu cầu hoàn tiền trong bao nhiêu ngày?",
        "Ai phải phê duyệt để cấp quyền Level 3?",
    ]

    print("\n--- Sprint 2: Test Variant ---")
    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            result = rag_answer(
                query,
                retrieval_mode="hybrid",
                top_k_search=15,
                top_k_select=3,
                use_rerank=False,
                verbose=True,
            )
            print(f"Answer: {result['answer']}")
            print(f"Sources: {result['sources']}")
        except Exception as e:
            print(f"Lỗi: {e}")
