"""
ID card detection stage.

Uses a local YOLOv8 model (via `ultralytics`) to locate an ID card in a
gate-camera frame. If no trained weights are present at models/best.pt,
falls back to a MOCK detector so the rest of the pipeline (OCR -> DB
lookup -> LLM -> image gen) is still fully runnable for demo/dev
purposes without a trained model.

To train your own detector:
  1. Label ~100-200 ID card images (Roboflow / LabelImg, class="id_card")
  2. yolo detect train data=data.yaml model=yolov8n.pt epochs=50
  3. Copy runs/detect/train/weights/best.pt -> models/best.pt
"""
import os

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "models", "best.pt")


class IDCardDetector:
    def __init__(self, model_path: str = MODEL_PATH, conf: float = 0.4):
        self.conf = conf
        self.model = None
        if os.path.exists(model_path):
            try:
                from ultralytics import YOLO
                self.model = YOLO(model_path)
                print(f"[detector] Loaded YOLOv8 weights from {model_path}")
            except Exception as e:
                print(f"[detector] Could not load YOLO weights ({e}). Using mock detector.")
        else:
            print(f"[detector] No weights found at {model_path}. Using mock detector "
                  f"(treats the whole input image as the card region).")

    def detect(self, image_path: str):
        """
        Returns a list of bounding boxes: [{"bbox": (x1, y1, x2, y2), "conf": float}]
        In mock mode, returns a single box covering the full image.
        """
        if self.model is not None:
            results = self.model.predict(image_path, conf=self.conf, verbose=False)
            boxes = []
            for r in results:
                for b in r.boxes:
                    x1, y1, x2, y2 = b.xyxy[0].tolist()
                    boxes.append({"bbox": (x1, y1, x2, y2), "conf": float(b.conf[0])})
            return boxes

        # Mock fallback
        from PIL import Image
        with Image.open(image_path) as img:
            w, h = img.size
        return [{"bbox": (0, 0, w, h), "conf": 1.0}]
