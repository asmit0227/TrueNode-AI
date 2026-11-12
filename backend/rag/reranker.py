from sentence_transformers import CrossEncoder


class Reranker:

    def __init__(self):

        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L6-v2"
        )

    def rerank(self, question, results, top_k=3):

        if not results:
            return []

        # Step 1: Create question-document pairs
        pairs = []

        for result in results:

            pairs.append(
                (question, result["text"])
            )

        # Step 2: Generate relevance scores
        scores = self.model.predict(pairs)

        # Step 3: Attach scores to results
        for i in range(len(results)):

            results[i]["rerank_score"] = float(scores[i])

        # Step 4: Sort results by relevance
        results.sort(
            key=lambda x: x["rerank_score"],
            reverse=True
        )

        # Step 5: Select best chunks
        final_results = results[:top_k]

        print("\nRERANKED RESULTS")

        for result in final_results:

            print(
                result["metadata"].get("source", "Unknown"),
                round(result["rerank_score"], 4)
            )

        return final_results