from backend.ingestion.loader import document_loader
from backend.ingestion.cleaner import TextCleaner
from backend.ingestion.chunker import Document_chunker


class DocumentIngestionPipeline:

    def __init__(self):
        self.cleaner = TextCleaner()
        self.chunker = Document_chunker(
            chunk_size=500,
            chunk_overlap=100
        )

    def process(self, file_path: str) :

        #  Load document
        loader = document_loader(file_path)
        documents = loader.load()

        #  Clean extracted text
        cleaned_documents = []

        for document in documents:

            cleaned_text = self.cleaner.clean(
                document["text"]
            )

            if not cleaned_text:
                continue

            cleaned_documents.append({
                "text": cleaned_text,
                "metadata": document["metadata"]
            })

         # Split into chunks
        chunks = self.chunker.split_documents(
            cleaned_documents
        )

        return chunks