import re
from rank_bm25 import BM25Okapi


class HybridSearch:

    def __init__(self, vector_store):

        self.vector_store = vector_store

    def search(self, question, query_embedding, top_k=3):

        db = self.vector_store.client
        collection = self.vector_store.collection_name

        # Step 1: Semantic Search
        dense_results = db.query_points(
            collection_name=collection,
            query=query_embedding,
            limit=10,
            with_payload=True
        ).points

        # Step 2: Get document chunks for BM25
        all_points = []
        offset = None

        while True:

            points, offset = db.scroll(
                collection_name=collection,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )

            all_points.extend(points)

            if offset is None:
                break

        # Keep chunks with readable text
        all_points = [
            point for point in all_points
            if (point.payload or {}).get("text", "").strip()
        ]

        if not all_points:
            return []

        # Step 3: Prepare text for BM25
        texts = [
            point.payload["text"]
            for point in all_points
        ]

        tokenized_texts = [
            re.findall(r"\w+", text.lower())
            for text in texts
        ]

        bm25 = BM25Okapi(tokenized_texts)

        # Step 4: Keyword Search
        query_tokens = re.findall(r"\w+", question.lower())

        keyword_scores = bm25.get_scores(query_tokens)

        keyword_results = sorted(
            zip(keyword_scores, all_points),
            key=lambda item: item[0],
            reverse=True
        )[:10]

        # Step 5: Combine rankings using RRF
        scores = {}
        point_lookup = {}

        # Add semantic search rankings
        for rank, point in enumerate(dense_results, start=1):

            point_id = str(point.id)

            scores[point_id] = 1 / (60 + rank)

            point_lookup[point_id] = point

        # Add BM25 rankings
        for rank, (score, point) in enumerate(keyword_results, start=1):

            if score <= 0:
                continue

            point_id = str(point.id)

            if point_id not in scores:
                scores[point_id] = 0

            scores[point_id] += 1 / (60 + rank)

            point_lookup[point_id] = point

        # Step 6: Sort combined results
        ranked_ids = sorted(
            scores,
            key=scores.get,
            reverse=True
        )

        # Step 7: Return Top-K results
        final_results = []

        for point_id in ranked_ids[:top_k]:

            point = point_lookup[point_id]

            payload = point.payload or {}

            metadata = {
                key: value
                for key, value in payload.items()
                if key != "text"
            }

            final_results.append({
                "text": payload.get("text", ""),
                "metadata": metadata,
                "rank_score": scores[point_id]
            })

        print("\nHYBRID SEARCH RESULTS")

        for result in final_results:

            print(
                result["metadata"].get("source", "Unknown"),
                round(result["rank_score"], 5)
            )

        return final_results