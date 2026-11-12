import re

from backend.rag.embeddings import Generate_embeddings
from backend.rag.vector_store import Vector_Store
from backend.rag.LLM import LLM
from backend.rag.hybrid_search import HybridSearch
from backend.rag.reranker import Reranker


class RAGPipeline:

    def __init__(self):

        self.embedding_model = Generate_embeddings()

        self.vector_store = Vector_Store()

        self.llm = LLM()

        self.hybrid_search = HybridSearch(
            self.vector_store
        )

        self.reranker = Reranker()


    def ask(self, question, include_context=False):

        # Step 1: Query Embedding
        query_embedding = self.embedding_model.query_embeddings(
            question
        )

        # Step 2: Hybrid Search
        results = self.hybrid_search.search(
            question,
            query_embedding,
            top_k=10
        )

        # Step 3: Cross-Encoder Reranking
        results = self.reranker.rerank(
            question,
            results,
            top_k=3
        )

        # Step 4: Handle Empty Results
        fallback = "I could not find this information in the documents."

        if not results:

            response = {
                "answer": fallback,
                "sources": []
            }

            if include_context:
                response["context"] = ""

            return response

        # Step 5: Build Context with Citation IDs
        context = ""
        source_map = {}

        for i, result in enumerate(results, start=1):

            source = result["metadata"].get(
                "source",
                "Unknown"
            )

            text = result["text"]

            citation_id = f"S{i}"

            source_map[citation_id] = source

            context += f"[{citation_id}] Source: {source}\n"
            context += text + "\n\n"

        # Step 6: Generate Answer
        answer = self.llm.generate_answer(
            question,
            context
        )
        print("\n========== RAW LLM ANSWER ==========")
        print(repr(answer))

        # Step 7: Extract Citation IDs
        cited_ids = re.findall(
            r"\[\s*S(\d+)\s*\]",
            answer,
            flags=re.IGNORECASE
            )
        print("Extracted Citation IDs:", cited_ids)
        print("Available Source IDs:", source_map)

        # Step 8: Get Cited Sources
        sources = []

        valid_ids = True

        for number in cited_ids:

            citation_id = "S" + number

            if citation_id not in source_map:
                valid_ids = False
                break

            source = source_map[citation_id]

            if source not in sources:
                sources.append(source)

        # Step 9: Handle Refusal or Invalid Citations
        if answer.strip().lower() == fallback.lower():

            sources = []

        elif not cited_ids or not valid_ids:

            # Do not present an answer with missing
            # or invalid citation references.
            answer = "I could not verify the citations for this answer."
            sources = []

        # Step 10: Prepare Response
        response = {
            "answer": answer,
            "sources": sources
        }

        if include_context:
            response["context"] = context

        return response


    def close(self):

        self.vector_store.close()