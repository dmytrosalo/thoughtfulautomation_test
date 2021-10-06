import re
from pdfminer.high_level import extract_text


class PDFParser:
    def __init__(self, file_path):
        self.text = extract_text(file_path)

    def get_by_key(self, key):
        matches = re.findall(f"{key}.*", self.text)
        return matches[0].split(':')[1].strip()

