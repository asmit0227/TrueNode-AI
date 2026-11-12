import os

from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from qdrant_client import QdrantClient, models


load_dotenv()


class Vector_Store:

    def __init__(
        self,
        collection_name: str = "Enterprise Evaluation",
        vector_size: int = 384
    ):

        self.collection_name = collection_name

        # Qdrant Cloud Configuration
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")

        # Cloud connection
        if qdrant_url and qdrant_api_key:

            print("Connecting to Qdrant Cloud...")

            self.client = QdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key
            )

            print("Qdrant Cloud Connected Successfully!")

        # Check incomplete configuration
        elif qdrant_url or qdrant_api_key:

            raise ValueError(
                "Both QDRANT_URL and QDRANT_API_KEY are required."
            )

        # Local connection for development
        else:

            print("Using Local Qdrant Storage...")

            db_path = Path("data/qdrant_db")
            db_path.mkdir(parents=True, exist_ok=True)

            self.client = QdrantClient(
                path=str(db_path)
            )

        # Create collection if it does not exist
        if not self.client.collection_exists(
            collection_name=self.collection_name
        ):

            self.client.create_collection(

                collection_name=self.collection_name,

                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE
                )
            )

            print("Qdrant Collection Created Successfully!")

    # Add Documents

    def add_documents(
        self,
        chunks: list[dict],
        embeddings: list[list[float]]
    ):

        if len(chunks) != len(embeddings):

            raise ValueError(
                "Chunks and embeddings count not matched!"
            )

        if not chunks:
            return 0

        points = []

        for chunk, embedding in zip(chunks, embeddings):

            point = models.PointStruct(

                id=str(uuid4()),

                vector=embedding,

                payload={
                    "text": chunk["text"],
                    **chunk["metadata"]
                }
            )

            points.append(point)

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        return len(points)

    # Search

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 3
    ):

        result = self.client.query_points(

            collection_name=self.collection_name,

            query=query_embedding,

            limit=top_k,

            with_payload=True
        )

        return [

            {
                "score": point.score,

                "text": point.payload.get("text", ""),

                "metadata": {
                    key: value
                    for key, value in point.payload.items()
                    if key != "text"
                }
            }

            for point in result.points
        ]

    # Count Documents

    def count_documents(self):

        result = self.client.count(

            collection_name=self.collection_name,

            exact=True
        )

        return result.count

    
    # Close Connection

    def close(self):

        self.client.close()





          


