patterns = []



class PdfManager:
    def __init__(self, pdf_raw_path="/data/datasets/sequias_historicas/raw/"):
        self.pdf_raw_path = pdf_raw_path

    def extract_text(self):
        # Placeholder for text extraction logic
        pass

    def save_text(self, text, output_path):
        # Placeholder for saving extracted text logic
        pass

    def _validate_newspaper(self, newspaper):
        if newspaper not in ["extremadura", "hoy"]:
            raise ValueError(f"Newspaper '{newspaper}' is not supported.")
        pass

    def list_pdfs(self,newspaper="extremadura", year=None):
        self._validate_newspaper(newspaper)
        lines=0
        with open(f"{self.pdf_raw_path}/{newspaper}.txt", "r") as f:
            for line in f:
                if year is None or line.startswith(f"{year}-"):
                    patterns.append(line.strip())
                    lines+=1
        print(f"Found {lines} PDFs for newspaper '{newspaper}' with year filter '{year}'")
        pass