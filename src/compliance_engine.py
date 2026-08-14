"""
Core orchestration: given a gate-camera frame, runs the full pipeline
and returns a structured result describing compliance status, and (if
non-compliant) the generated LLM report + Stable Diffusion alert visual.
"""
import os
import datetime

from src.detector import IDCardDetector
from src.ocr_reader import CardOCR
from src.db_manager import LibraryDB
from src.llm_report import generate_incident_report
from src.image_alert import generate_alert_visual

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "outputs", "reports")


class ComplianceEngine:
    def __init__(self, gate_id: str = "Main Gate"):
        self.gate_id = gate_id
        self.detector = IDCardDetector()
        self.ocr = CardOCR()
        self.db = LibraryDB()

    def process_frame(self, image_path: str) -> dict:
        detections = self.detector.detect(image_path)
        if not detections:
            return self._flag(reg_no=None, reason="No ID card detected in frame")

        # Assume single-card gate (extend to loop for multi-card frames)
        ocr_result = self.ocr.read(image_path)
        reg_no = ocr_result.get("reg_no")

        profile = self.db.lookup(reg_no)
        if profile is None:
            return self._flag(reg_no=reg_no, reason="Reg. No. not found in library database")
        if profile["library_status"] != "ACTIVE":
            return self._flag(reg_no=reg_no,
                               reason=f"Library status is {profile['library_status']}")
        if profile["is_expired"]:
            return self._flag(reg_no=reg_no,
                               reason=f"Card expired on {profile['card_expiry']}")

        return {
            "compliant": True,
            "reg_no": reg_no,
            "name": profile["name"],
            "department": profile["department"],
            "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        }

    def _flag(self, reg_no, reason) -> dict:
        event = {"gate_id": self.gate_id, "reg_no": reg_no or "UNKNOWN", "reason": reason}
        report_text = generate_incident_report(event)
        alert_path = generate_alert_visual(event)

        os.makedirs(REPORTS_DIR, exist_ok=True)
        report_path = os.path.join(
            REPORTS_DIR, f"report_{event['reg_no']}_"
                         f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        with open(report_path, "w") as f:
            f.write(report_text)

        return {
            "compliant": False,
            "reg_no": reg_no,
            "reason": reason,
            "report_text": report_text,
            "report_path": report_path,
            "alert_image_path": alert_path,
            "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        }
