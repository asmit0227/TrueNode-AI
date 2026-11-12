import os

from pathlib import Path
from dotenv import load_dotenv

from qdrant_client import QdrantClient, models


# Load environment variables
load_dotenv()


COLLECTION_NAME = "Enterprise Evaluation"

LOCAL_PATH = Path("data/qdrant_db")


def migrate_qdrant():

    local_client = None
    cloud_client = None

    try:

        # 1. Check Cloud Credentials

        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")

        if not qdrant_url or not qdrant_api_key:

            raise ValueError(
                "QDRANT_URL or QDRANT_API_KEY missing in .env"
            )

        print("Cloud credentials found.")

        # 2. Connect to Local Qdrant

        if not LOCAL_PATH.exists():

            raise FileNotFoundError(
                "Local Qdrant database not found!"
            )

        print("\nConnecting to Local Qdrant...")

        local_client = QdrantClient(
            path=str(LOCAL_PATH)
        )

        if not local_client.collection_exists(
            COLLECTION_NAME
        ):

            collections = [
                item.name
                for item in local_client.get_collections().collections
            ]

            raise ValueError(
                f"Collection not found. Available: {collections}"
            )

        print("Local Qdrant Connected!")

        # 3. Get Local Collection Details

        local_info = local_client.get_collection(
            COLLECTION_NAME
        )

        local_vector_config = (
            local_info.config.params.vectors
        )

        if not hasattr(local_vector_config, "size"):

            raise ValueError(
                "Named or multi-vector collection detected. "
                "This migration script expects a single vector."
            )

        local_count = local_client.count(
            collection_name=COLLECTION_NAME,
            exact=True
        ).count

        print("Collection:", COLLECTION_NAME)
        print("Local Points:", local_count)
        print("Vector Dimensions:", local_vector_config.size)

        if local_count == 0:

            raise ValueError(
                "Local collection contains no points. "
                "Migration stopped."
            )

        # 4. Connect to Qdrant Cloud

        print("\nConnecting to Qdrant Cloud...")

        cloud_client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key
        )

        print("Qdrant Cloud Connected!")

        # 5. Create Cloud Collection

        if cloud_client.collection_exists(
            COLLECTION_NAME
        ):

            cloud_info = cloud_client.get_collection(
                COLLECTION_NAME
            )

            cloud_count = cloud_client.count(
                collection_name=COLLECTION_NAME,
                exact=True
            ).count

            if cloud_count > 0:

                raise ValueError(
                    f"Cloud collection already contains "
                    f"{cloud_count} points. Migration stopped "
                    "to avoid overwriting existing data."
                )

            cloud_vector_config = (
                cloud_info.config.params.vectors
            )

            if (
                not hasattr(cloud_vector_config, "size")
                or cloud_vector_config.size != local_vector_config.size
                or cloud_vector_config.distance != local_vector_config.distance
            ):

                raise ValueError(
                    "Cloud collection configuration "
                    "does not match local collection."
                )

            print("Empty Cloud Collection already exists.")

        else:

            cloud_client.create_collection(

                collection_name=COLLECTION_NAME,

                vectors_config=models.VectorParams(

                    size=local_vector_config.size,

                    distance=local_vector_config.distance

                )
            )

            print("Cloud Collection Created!")

        # 6. Transfer Local Points

        print("\nStarting Migration...")

        offset = None

        migrated = 0

        while True:

            points, next_offset = local_client.scroll(

                collection_name=COLLECTION_NAME,

                limit=100,

                offset=offset,

                with_payload=True,

                with_vectors=True

            )

            if not points:
                break

            cloud_points = []

            for point in points:

                if point.vector is None:

                    raise ValueError(
                        f"Vector missing for point {point.id}"
                    )

                cloud_points.append(

                    models.PointStruct(

                        id=point.id,

                        vector=point.vector,

                        payload=point.payload or {}

                    )

                )

            cloud_client.upsert(

                collection_name=COLLECTION_NAME,

                points=cloud_points,

                wait=True

            )

            migrated += len(cloud_points)

            print(
                f"Migrated: {migrated}/{local_count}"
            )

            if next_offset is None:
                break

            offset = next_offset

        # 7. Verify Migration

        cloud_count = cloud_client.count(

            collection_name=COLLECTION_NAME,

            exact=True

        ).count

        print("\n========== MIGRATION SUMMARY ==========")

        print("Local Points:", local_count)

        print("Migrated Points:", migrated)

        print("Cloud Points:", cloud_count)

        if (
            migrated == local_count
            and cloud_count == local_count
        ):

            print("\nSUCCESS: Qdrant Migration Completed!")

        else:

            raise RuntimeError(
                "Migration verification failed. "
                "Local and Cloud counts do not match."
            )

    finally:

        if local_client:
            local_client.close()

        if cloud_client:
            cloud_client.close()


if __name__ == "__main__":

    migrate_qdrant()