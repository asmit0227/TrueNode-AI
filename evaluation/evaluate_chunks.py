from backend.core.resources import rag



# STEP 1: Evaluation Questions


questions = [
    {
        "question": "How many annual leave days do employees receive?",
        "evidence": [
            (
                "hr_leave_policy.txt",
                "Full-time employees receive 18 days of annual leave per year."
            )
        ]
    },

    {
        "question": "How many sick leave days do employees receive?",
        "evidence": [
            (
                "hr_leave_policy.txt",
                "Employees receive 10 days of paid sick leave annually."
            )
        ]
    },

    {
        "question": "Can employees work from home?",
        "evidence": [
            (
                "hr_leave_policy.txt",
                "Employees can request remote work arrangements with approval from their manager and HR department."
            )
        ]
    },

    {
        "question": "How can employees reset passwords?",
        "evidence": [
            (
                "it_support.txt",
                "Employees can reset their passwords using the company self-service portal."
            )
        ]
    },

    {
        "question": "Can employees share company passwords?",
        "evidence": [
            (
                "security_policy.txt",
                "Employees must not share company passwords."
            )
        ]
    },

    {
        "question": "Who approves remote work and restricted system access?",
        "evidence": [
            (
                "hr_leave_policy.txt",
                "Employees can request remote work arrangements with approval from their manager and HR department."
            ),
            (
                "access_policy.txt",
                "Restricted system access requires approval from the reporting manager and the system owner."
            )
        ]
    },

    {
        "question": "How do employees reset passwords and report security incidents?",
        "evidence": [
            (
                "it_support.txt",
                "Employees can reset their passwords using the company self-service portal."
            ),
            (
                "security_policy.txt",
                "Employees must report security incidents to the IT security team immediately."
            )
        ]
    }
]



# STEP 2: Normalize Text

def normalize(text):

    return " ".join(text.lower().split())


# STEP 3: Read All Qdrant Chunks

def get_all_chunks():

    chunks = []
    offset = None

    db = rag.vector_store.client
    collection = rag.vector_store.collection_name

    while True:

        points, offset = db.scroll(
            collection_name=collection,
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=False
        )

        chunks.extend(points)

        if offset is None:
            break

    return chunks


# STEP 4: Find Expected Chunk IDs

def find_expected_chunks(evidence, all_chunks):

    expected_ids = set()

    for source, sentence in evidence:

        matches = []

        for point in all_chunks:

            payload = point.payload or {}

            chunk_source = payload.get("source", "")
            chunk_text = payload.get("text", "")

            if (
                chunk_source == source
                and normalize(sentence) in normalize(chunk_text)
            ):
                matches.append(point)

        # Ground truth should identify exactly one chunk
        if len(matches) != 1:

            raise ValueError(
                f"Expected one matching chunk for {source}, "
                f"found {len(matches)}. Check the evidence text."
            )

        expected_ids.add(str(matches[0].id))

    return expected_ids


# STEP 5: Identify Retrieved Chunk IDs

def get_retrieved_ids(results, chunk_lookup):

    retrieved_ids = []

    for result in results[:3]:

        source = result["metadata"].get("source", "")
        text = result["text"]

        key = (source, normalize(text))

        chunk_id = chunk_lookup.get(key)

        if chunk_id is None:

            raise ValueError(
                f"Retrieved chunk not found in Qdrant: {source}"
            )

        retrieved_ids.append(chunk_id)

    return retrieved_ids


# STEP 6: Calculate Metrics


def calculate_metrics(retrieved, expected):

    relevant = set(retrieved) & expected

    hit = 1 if relevant else 0

    recall = len(relevant) / len(expected)

    precision = len(relevant) / 3

    reciprocal_rank = 0

    for rank, chunk_id in enumerate(retrieved, start=1):

        if chunk_id in expected:

            reciprocal_rank = 1 / rank
            break

    all_found = 1 if expected.issubset(set(retrieved)) else 0

    return hit, recall, precision, reciprocal_rank, all_found



# STEP 7: Run Evaluation

systems = ["Semantic", "Hybrid", "Reranked"]

scores = {}

for system in systems:

    scores[system] = {
        "hit": 0,
        "recall": 0,
        "precision": 0,
        "mrr": 0,
        "all_found": 0
    }


try:

    all_chunks = get_all_chunks()

    print("Total Qdrant Chunks:", len(all_chunks))

    # Map stored text to its point ID
    chunk_lookup = {}

    for point in all_chunks:

        payload = point.payload or {}

        key = (
            payload.get("source", ""),
            normalize(payload.get("text", ""))
        )

        if key in chunk_lookup:
            raise ValueError(
                "Duplicate source/text chunks found. "
                "Chunk IDs must be mapped explicitly."
            )

        chunk_lookup[key] = str(point.id)

    for item in questions:

        question = item["question"]

        print("\n" + "=" * 60)

        print("QUESTION:", question)

        expected_ids = find_expected_chunks(
            item["evidence"],
            all_chunks
        )

        print("Expected Chunk IDs:", expected_ids)

        # Query embedding
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

        # Cross-Encoder Reranking
        reranked_results = rag.reranker.rerank(
            question,
            hybrid_results.copy(),
            top_k=3
        )

        results = {
            "Semantic": semantic_results,
            "Hybrid": hybrid_results[:3],
            "Reranked": reranked_results
        }

        for system in systems:

            retrieved_ids = get_retrieved_ids(
                results[system],
                chunk_lookup
            )

            hit, recall, precision, mrr, all_found = calculate_metrics(
                retrieved_ids,
                expected_ids
            )

            scores[system]["hit"] += hit
            scores[system]["recall"] += recall
            scores[system]["precision"] += precision
            scores[system]["mrr"] += mrr
            scores[system]["all_found"] += all_found

            print(
                system,
                "| Recall:", round(recall, 3),
                "| Precision:", round(precision, 3),
                "| MRR:", round(mrr, 3)
            )

finally:

    rag.close()


# STEP 8: Final Report

total = len(questions)

print("\n========== CHUNK-LEVEL EVALUATION ==========")

print("Total Questions:", total)

for system in systems:

    result = scores[system]

    print("\nSystem:", system)

    print("Hit Rate@3:", round(result["hit"] / total, 4))

    print("Recall@3:", round(result["recall"] / total, 4))

    print("Precision@3:", round(result["precision"] / total, 4))

    print("MRR@3:", round(result["mrr"] / total, 4))

    print(
        "All Evidence Found@3:",
        round(result["all_found"] / total, 4)
    )