from sentence_transformers import SentenceTransformer

class Generate_embeddings:

    def __init__(self, model_name :str =  "sentence-transformers/all-MiniLM-L6-v2"):
        self.model=SentenceTransformer(model_name)

    def document_embeddings(self,texts:list[str]):

        if not texts:
            return []

        doc_embeddings=self.model.encode(texts,normalize_embeddings=True,show_progress_bar=False)

        return doc_embeddings.tolist()

    def query_embeddings(self,query:str):
        if not query:
            return []

        query_embedding= self.model.encode(query,normalize_embeddings=True,show_progress_bar=False)

        return query_embedding.tolist()

        