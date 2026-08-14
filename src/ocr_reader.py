"""
OCR stage: extracts Reg. No. and Name text from the cropped ID card
region produced by detector.py.

Uses EasyOCR (fully local, no cloud). If EasyOCR / its model weights
aren't available in the current environment, falls back to a regex
parse of the filename (works with the synthetic cards produced by
dummy_data_generator.py) so the demo still runs end-to-end.
"""
import os
import re


class CardOCR:
    def __init__(self, use_easyocr: bool = True, langs=("en",)):
        self.reader = None
        if use_easyocr:
            try:
                import easyocr
                self.reader = easyocr.Reader(list(langs), gpu=False)
                print("[ocr_reader] EasyOCR initialized.")
            except Exception as e:
                print(f"[ocr_reader] EasyOCR unavailable ({e}). Falling back to mock OCR.")

    def read(self, image_path: str) -> dict:
        """Returns {"reg_no": str, "name": str} best-effort."""
        if self.reader is not None:
            results = self.reader.readtext(image_path, detail=0)
            text = " ".join(results)
            reg_match = re.search(r"REG\d+", text, re.IGNORECASE)
            reg_no = reg_match.group(0).upper() if reg_match else None
            name_match = re.search(r"Name[:\s]+([A-Za-z .]+)", text)
            name = name_match.group(1).strip() if name_match else None
            return {"reg_no": reg_no, "name": name, "raw_text": text}

        # Mock fallback: parse the synthetic filename REGxxxx_card.png
        fname = os.path.basename(image_path)
        m = re.match(r"(REG\d+)_card", fname)
        reg_no = m.group(1) if m else None
        return {"reg_no": reg_no, "name": None, "raw_text": f"[mock ocr] {fname}"}
