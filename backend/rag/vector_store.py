from qdrant_client import QdrantClient , models
from uuid import uuid4
from pathlib import Path

class Vector_Store:
    def __init__(self,
              collection_name : str= "Enterprise Evaluation", 
              vector_size:int=384
    ):

        self.collection_name= collection_name

        #persistent storage 
        db_path=Path("data/qdrant_db")
        db_path.mkdir(parents=True,exist_ok=True)

        self.client=QdrantClient(path=str(db_path))


        if not self.client.collection_exists(collection_name=self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE

                )
            )

    def add_documents(self,chunks=list[dict],embeddings=list[list[float]]):

        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings count not matched!")      

        if not chunks:
            return 0

        points=[]

        for chunk,embedding in zip(chunks,embeddings):
            point=models.PointStruct(
                id=str(uuid4()),
                vector=embedding,
                payload={
                    "text":chunk["text"],
                    **chunk["metadata"]
                }
            )

            points.append(point)

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        ) 
        return len(points)


    def search(self,query_embedding :list[float],top_k:int=3):
        result= self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=top_k,
            with_payload=True
)
        
        return[
            { "score" : point.score,
              "text"  : point.payload.get("text",""),
              "metadata": {
                    key: value
                    for key, value in point.payload.items()
                    if key != "text"
                }
            }
            for point in result.points
        ]

    def count_documents(self):

        result= self.client.count(
            collection_name=self.collection_name,
            exact=True
        )
        return result.count

    def close(self):
        self.client.close()





          


