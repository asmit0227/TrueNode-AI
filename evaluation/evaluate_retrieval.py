from backend.core.resources import rag


# Step 1: Evaluation Dataset

questions = [
    {
        "question": "How many annual leave days do employees receive?",
        "expected_source": "hr_leave_policy.txt"
    },
    {
        "question": "Can employees work from home?",
        "expected_source": "hr_leave_policy.txt"
    },
    {
        "question": "How can employees reset passwords?",
        "expected_source": "it_support.txt"
    },
    {
        "question": "When should employees report lost laptops?",
        "expected_source": "it_support.txt"
    },
    {
        "question": "Can employees share company passwords?",
        "expected_source": "security_policy.txt"
    },
    {
        "question": "Who should employees report security incidents to?",
        "expected_source": "security_policy.txt"
    },
    {
        "question": "What are the company's office hours?",
        "expected_source": "employee_handbook.txt"
    },
    {
        "question": "How should employees mark attendance?",
        "expected_source": "employee_handbook.txt"
    }
]


# Step 2: Calculate metrics for one question

def calculate_metrics(results, expected_source):

    for rank, result in enumerate(results[:3], start=1):

        source = result["metadata"].get("source")

        if source == expected_source:

            hit = 1
            reciprocal_rank = 1 / rank

            return hit, reciprocal_rank

    return 0, 0


# Step 3: Compare retrieval systems

scores = {
    "Semantic": {"hits": 0, "mrr": 0},
    "Hybrid": {"hits": 0, "mrr": 0},
    "Reranked": {"hits": 0, "mrr": 0}
}


try:

    for item in questions:

        question = item["question"]
        expected = item["expected_source"]

        print("\nQuestion:", question)

        # Generate query embedding
        query_embedding = rag.embedding_model.query_embeddings(
            question
        )

        # Semantic Search
        semantic_results = rag.vector_store.search(
            query_embedding,
            top_k=3
        )

        # Hybrid Search
        hybrid_results = rag.hybrid_search.search(
            question,
            query_embedding,
            top_k=10
        )

        # Reranking
        reranked_results = rag.reranker.rerank(
            question,
            hybrid_results.copy(),
            top_k=3
        )

        # Evaluate all systems
        systems = {
            "Semantic": semantic_results,
            "Hybrid": hybrid_results[:3],
            "Reranked": reranked_results
        }

        for name, results in systems.items():

            hit, mrr = calculate_metrics(
                results,
                expected
            )

            scores[name]["hits"] += hit
            scores[name]["mrr"] += mrr

            print(name, "| Hit:", hit, "| RR:", round(mrr, 3))


    # Step 4: Final Results

    total = len(questions)

    print("\n========== FINAL EVALUATION ==========")

    for name, result in scores.items():

        hit_rate = result["hits"] / total
        mrr = result["mrr"] / total

        print("\nSystem:", name)
        print("Hit Rate@3:", round(hit_rate, 4))
        print("MRR@3:", round(mrr, 4))

finally:

    rag.close()