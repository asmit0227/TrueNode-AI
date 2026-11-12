from pathlib import Path
from uuid import uuid4
import traceback

from fastapi import APIRouter, UploadFile, File, HTTPException

import traceback

from backend.ingestion.pipeline import DocumentIngestionPipeline
from backend.core.resources import rag
from qdrant_client import models
import hashlib
from fastapi import Depends
from backend.core.security import require_admin, get_current_user


router = APIRouter()

pipeline = DocumentIngestionPipeline()

UPLOAD_FOLDER = Path("data/uploads")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

MAX_SIZE = 10 * 1024 * 1024


@router.post("/upload",dependencies=[Depends(require_admin)])
def upload_document(file: UploadFile = File(...)):

    # Step 1: Check file extension
    original_name = Path(file.filename or "").name

    extension = Path(original_name).suffix.lower()

    if extension not in [".pdf", ".docx", ".txt"]:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOCX and TXT files are allowed"
        )

    # Step 2: Generate document ID
    file_id = str(uuid4())

    file_path = UPLOAD_FOLDER / f"{file_id}{extension}"

    try:

        # Step 3: Read uploaded file
        content = file.file.read(MAX_SIZE + 1)

        if len(content) > MAX_SIZE:
            raise HTTPException(
                status_code=413,
                detail="Maximum file size is 10 MB"
            )
        # Generate file hash
        file_hash = hashlib.sha256(content).hexdigest()

        print("File Hash:", file_hash)


        # Check duplicate document
        db = rag.vector_store.client

        collection = rag.vector_store.collection_name

        duplicate_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="file_hash",
                    match=models.MatchValue(value=file_hash)
                )
            ]
        )

        result = db.count(
            collection_name=collection,
            count_filter=duplicate_filter,
            exact=True
        )

        if result.count > 0:
            raise HTTPException(
                status_code=409,
                detail="This document already exists"
            )

        # Step 4: Save file
        with open(file_path, "wb") as saved_file:
            saved_file.write(content)

        # Step 5: Process document
        print("\n[1] Processing uploaded document...")
        chunks = pipeline.process(str(file_path))
        print("Total Chunks:", len(chunks))

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No readable text found"
            )

        # Step 6: Update metadata
        for chunk in chunks:

            chunk["metadata"]["source"] = original_name
            chunk["metadata"]["document_id"] = file_id
            chunk["metadata"]["file_hash"] = file_hash

        # Step 7: Generate embeddings
        texts = [chunk["text"] for chunk in chunks]

        print("\n[2] Generating embeddings...")
        embeddings = rag.embedding_model.document_embeddings(texts)
        print("Total Embeddings:", len(embeddings))

        # Step 8: Store in shared Qdrant
        print("\n[3] Storing vectors in Qdrant...")
        inserted = rag.vector_store.add_documents(chunks,embeddings)
        print("Inserted Vectors:", inserted)

        return {
            "message": "Document uploaded successfully",
            "document_id": file_id,
            "filename": original_name,
            "total_chunks": inserted,
            "status": "indexed"
        }

    except HTTPException:
        raise

    except Exception as error:


        print("\n========== UPLOAD ERROR ==========")

        print("Error Type:", type(error).__name__)

        print("Error Message:", str(error))

        traceback.print_exc()

        print("==================================\n")

        raise HTTPException(
            status_code=500,
            detail="Document processing failed"
        ) from error

@router.get("/",dependencies=[Depends(get_current_user)])
def list_documents():

    documents = {}

    offset = None

    while True:

        points, offset = rag.vector_store.client.scroll(
            collection_name=rag.vector_store.collection_name,
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=False
        )

        for point in points:

            metadata = point.payload or {}

            document_id = metadata.get("document_id")

            filename = metadata.get("source", "Unknown")

            # Older documents may not have document_id
            key = document_id or "legacy:" + filename

            if key not in documents:

                documents[key] = {
                    "document_id": document_id,
                    "filename": filename,
                    "total_chunks": 0
                }

            documents[key]["total_chunks"] += 1

        if offset is None:
            break

    return {
        "total_documents": len(documents),
        "documents": list(documents.values())
    }

@router.delete("/{document_id}",dependencies=[Depends(require_admin)])
def delete_document(document_id: str):

    # Step 1: Connect to shared Qdrant
    db = rag.vector_store.client

    collection = rag.vector_store.collection_name

    # Step 2: Find document by ID
    document_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="document_id",
                match=models.MatchValue(
                    value=document_id
                )
            )
        ]
    )

    # Step 3: Check document exists
    result = db.count(
        collection_name=collection,
        count_filter=document_filter,
        exact=True
    )

    if result.count == 0:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # Step 4: Delete document chunks
    db.delete(
        collection_name=collection,
        points_selector=models.FilterSelector(
            filter=document_filter
        ),
        wait=True
    )

    # Step 5: Return success response
    return {
        "message": "Document deleted successfully",
        "document_id": document_id,
        "deleted_chunks": result.count
    }

     