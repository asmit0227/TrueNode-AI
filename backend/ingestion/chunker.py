from langchain_text_splitters import RecursiveCharacterTextSplitter


class Document_chunker():

    def __init__(self,chunk_size:int=500,chunk_overlap:int=100):
        if chunk_size<=0:
            raise ValueError("chunk_size must be positive")

        if chunk_overlap<0 or chunk_overlap>=chunk_size:
            raise ValueError(
                "chunk_overlap must be >= 0 and smaller than chunk_size"
            )

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def split_documents(self, documents: list[dict]) :

        all_chunks = []

        for document in documents:

            text = document["text"]
            metadata = document["metadata"]

            chunks = self.splitter.split_text(text)

            for index, chunk in enumerate(chunks):

                all_chunks.append({
                    "text": chunk,
                    "metadata": {
                        **metadata,
                        "chunk_index": index,
                        "chunk_size": len(chunk)
                    }
                })

        return all_chunks