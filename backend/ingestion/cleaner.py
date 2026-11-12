import re


class TextCleaner:

    @staticmethod
    def clean(text: str) -> str:
        if not text:
            return ""

        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Remove unwanted control characters
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

        # Normalize multiple spaces and tabs
        text = re.sub(r"[ \t]+", " ", text)

        # Join words broken across lines by hyphens
        text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

        # Reduce excessive blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()