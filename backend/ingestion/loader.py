from pathlib import Path
from datetime import datetime,timezone

import pymupdf
from docx import Document

class document_loader:

    SUPPORTED_FORMATS = {".pdf",".docx",".txt"}
    def __init__(self,filepath:str):

        self.pathfile=Path(filepath)

        if not self.pathfile.is_file():
            raise FileNotFoundError(
                f"file not found : {self.filepath}"
            )

        if self.pathfile.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format"
            )

    def extract_pdf(self):
        document=[]

        with pymupdf.open(self.pathfile) as pdf:
            for page_number , page in enumerate(pdf,start=1):
                text = page.get_text("text",sort=True)
                if not text.strip():
                    continue

                document.append({
                    "text":text,
                    "page_number":page_number
                })
        return document

    def extract_docx(self):
        document=Document(self.pathfile)

        text_parts = []

        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)

        for table in document.tables:
            for row in table.rows:
                cells=[cell.text.strip()
                       for cell in row.cells]    

                text_parts.append(" | ".join(cells)) 

        return [{
            "text":"\n".join(text_parts),
            "page_number":None
        }]   


    def extract_txt(self):
        text = self.pathfile.read_text(
            encoding="utf-8-sig"
        )    

        return [{
            "text": text,
            "page_number": None
        }]  

    def load(self):

        extension = self.pathfile.suffix.lower()

        if extension == ".pdf":
            extracted_data = self.extract_pdf()

        elif extension == ".docx":
            extracted_data = self.extract_docx()

        else:
            extracted_data = self.extract_txt()

        documents = []

        for item in extracted_data:

            if not item["text"].strip():
                continue

            documents.append({

                "text": item["text"],

                "metadata": {
                    "source": self.pathfile.name,
                    "file_type": extension,
                    "page_number": item["page_number"],
                    "processed_at": datetime.now(
                        timezone.utc
                    ).isoformat()
                }
            })

        return documents  

