import json
import csv
import time
import math

from backend.core.resources import rag


# STEP 1: Load Golden Dataset

with open(
    "evaluation/golden_dataset.json",
    "r",
    encoding="utf-8"
) as file:

    questions = json.load(file)


print("Total Evaluation Questions:", len(questions))


# STEP 2: Get unique document names from search results

def get_sources(results, top_k=3):

    sources = []

    for result in results:

        source = result["metadata"].get("source")

        if source and source not in sources:
            sources.append(source)

        if len(sources) == top_k:
            break

    return sources


# STEP 3: Calculate Evaluation Metrics

def calculate_metrics(sources, expected):

    relevant = 0
    reciprocal_rank = 0

    for rank, source in enumerate(sources, start=1):

        if source in expected:

            relevant += 1

            if reciprocal_rank == 0:
                reciprocal_rank = 1 / rank

    hit = 1 if relevant > 0 else 0

    recall = relevant / len(expected)

    precision = relevant / len(sources) if sources else 0

    all_found = 1 if relevant == len(expected) else 0

    return hit, recall, precision, reciprocal_rank, all_found


# STEP 4: Calculate P95 Latency

def calculate_p95(times):

    if not times:
        return 0

    times = sorted(times)

    index = math.ceil(0.95 * len(times)) - 1

    return times[index]


# STEP 5: Initialize Results

systems = ["Semantic", "Hybrid", "Reranked"]

splits = ["dev", "test"]

scores = {}

for split in splits:

    scores[split] = {}

    for system in systems:

        scores[split][system] = {
            "count": 0,
            "hit": 0,
            "recall": 0,
            "precision": 0,
            "mrr": 0,
            "all_found": 0,
            "latencies": []
        }


csv_results = []
skipped = 0


# STEP 6: Run Evaluation

try:

    for item in questions:

        question = item["question"]

        expected = item["expected_sources"]

        split = item["split"]

        # Unanswerable questions need separate refusal evaluation
        if not expected:

            skipped += 1
            continue

        print("\n" + "=" * 60)

        print("Question:", question)

        print("Expected:", expected)

        # Generate query embedding
        query_embedding = rag.embedding_model.query_embeddings(
            question
        )

        # Semantic Search

        start = time.perf_counter()

        semantic_results = rag.vector_store.search(
            query_embedding,
            top_k=10
        )

        semantic_time = time.perf_counter() - start

        # Hybrid Search

        start = time.perf_counter()

        hybrid_results = rag.hybrid_search.search(
            question,
            query_embedding,
            top_k=10
        )

        hybrid_time = time.perf_counter() - start

        # Cross-Encoder Reranking

        start = time.perf_counter()

        reranked_results = rag.reranker.rerank(
            question,
            hybrid_results.copy(),
            top_k=10
        )

        rerank_time = time.perf_counter() - start

        # Hybrid + Reranking total retrieval time
        total_rerank_time = hybrid_time + rerank_time

        # Compare systems

        results = {
            "Semantic": semantic_results,
            "Hybrid": hybrid_results,
            "Reranked": reranked_results
        }

        latencies = {
            "Semantic": semantic_time,
            "Hybrid": hybrid_time,
            "Reranked": total_rerank_time
        }

        for name in systems:

            sources = get_sources(
                results[name],
                top_k=3
            )

            hit, recall, precision, mrr, all_found = calculate_metrics(
                sources,
                expected
            )

            score = scores[split][name]

            score["count"] += 1
            score["hit"] += hit
            score["recall"] += recall
            score["precision"] += precision
            score["mrr"] += mrr
            score["all_found"] += all_found

            score["latencies"].append(
                latencies[name]
            )

            print(
                name,
                "| Recall:", round(recall, 3),
                "| Precision:", round(precision, 3),
                "| MRR:", round(mrr, 3)
            )

            csv_results.append({
                "question": question,
                "split": split,
                "system": name,
                "expected_sources": ", ".join(expected),
                "retrieved_sources": ", ".join(sources),
                "hit": hit,
                "recall": recall,
                "precision": precision,
                "mrr": mrr,
                "all_found": all_found,
                "latency": round(latencies[name], 4)
            })

finally:

    rag.close()


# STEP 7: Final Evaluation Results

print("\n========== FINAL GOLDEN EVALUATION ==========")

print("Unanswerable Questions Skipped:", skipped)

for split in splits:

    print("\nDATASET SPLIT:", split.upper())

    for name in systems:

        result = scores[split][name]

        total = result["count"]

        if total == 0:
            continue

        print("\nSystem:", name)

        print("Questions:", total)

        print("Hit Rate@3:",
              round(result["hit"] / total, 4))

        print("Recall@3:",
              round(result["recall"] / total, 4))

        print("Precision@3:",
              round(result["precision"] / total, 4))

        print("MRR@3:",
              round(result["mrr"] / total, 4))

        print("All Sources Found@3:",
              round(result["all_found"] / total, 4))

        print("Average Latency:",
              round(sum(result["latencies"]) / total, 4))

        print("P95 Latency:",
              round(calculate_p95(result["latencies"]), 4))


# STEP 8: Save CSV Results

with open(
    "evaluation/golden_results.csv",
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "question",
            "split",
            "system",
            "expected_sources",
            "retrieved_sources",
            "hit",
            "recall",
            "precision",
            "mrr",
            "all_found",
            "latency"
        ]
    )

    writer.writeheader()

    writer.writerows(csv_results)


print("\nEvaluation results saved successfully!")