"""
Local image generation stage: for every non-compliant event, generates
a stylized security alert graphic (NOT a photo of the student - a
generic warning/notice visual) using a local Stable Diffusion install
via the AUTOMATIC1111 WebUI API (http://127.0.0.1:7860), no cloud calls.

Start the local API with:  ./webui.sh --api   (or webui-user.bat --api on Windows)

Falls back to a simple PIL-drawn placeholder alert card if the local
Stable Diffusion API isn't reachable, so the pipeline still produces
an output file during development/demo.
"""
import os
import base64
import datetime
import requests

SD_API_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "outputs", "alerts")


def _placeholder_alert(event: dict, out_path: str):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (512, 512), color=(40, 10, 10))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
        font_small = ImageFont.truetype("DejaVuSans.ttf", 18)
    except IOError:
        font = font_small = ImageFont.load_default()

    draw.rectangle([10, 10, 501, 501], outline=(220, 60, 60), width=6)
    draw.text((40, 40), "ACCESS DENIED", fill=(230, 60, 60), font=font)
    draw.text((40, 100), f"Reg No: {event.get('reg_no', 'UNKNOWN')}", fill="white", font=font_small)
    draw.text((40, 130), f"Reason: {event.get('reason', 'Non-compliant')}", fill="white", font=font_small)
    draw.text((40, 160), f"Gate: {event.get('gate_id', 'Main Gate')}", fill="white", font=font_small)
    draw.text((40, 460), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               fill=(180, 180, 180), font=font_small)
    img.save(out_path)


def generate_alert_visual(event: dict, out_dir: str = OUT_DIR) -> str:
    os.makedirs(out_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    reg_no = event.get("reg_no", "UNKNOWN")
    out_path = os.path.join(out_dir, f"alert_{reg_no}_{timestamp}.png")

    prompt = (
        "flat vector security alert icon, red warning triangle, campus gate "
        "access denied notice, minimal poster design, no text, no faces"
    )
    payload = {
        "prompt": prompt,
        "negative_prompt": "text, watermark, faces, photorealistic person",
        "steps": 20,
        "width": 512,
        "height": 512,
    }

    try:
        resp = requests.post(SD_API_URL, json=payload, timeout=15)
        resp.raise_for_status()
        image_b64 = resp.json()["images"][0]
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(image_b64))
        print(f"[image_alert] Stable Diffusion alert saved -> {out_path}")
    except Exception as e:
        print(f"[image_alert] Local SD API unavailable ({e}). Using placeholder alert card.")
        _placeholder_alert(event, out_path)

    return out_path
