"""
Generates dummy data so the project runs end-to-end without a real
camera feed, real student database, or real ID card photos:

  1. data/library_profiles.csv  -> fake "library system" records
  2. data/sample_id_cards/*.png -> synthetic ID card images (drawn, not
     photographed) that the detector/OCR stages can run against

Run:  python -m src.dummy_data_generator
"""
import os
import csv
import random
from datetime import datetime, timedelta

from PIL import Image, ImageDraw, ImageFont
from faker import Faker

fake = Faker()
random.seed(42)
Faker.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CARDS_DIR = os.path.join(DATA_DIR, "sample_id_cards")

DEPARTMENTS = ["CSE", "ECE", "MECH", "CIVIL", "MBA", "DATA-ANALYTICS"]


def generate_library_profiles(n=25, out_path=None):
    """Creates a CSV that mimics an existing library system export."""
    out_path = out_path or os.path.join(DATA_DIR, "library_profiles.csv")
    rows = []
    for i in range(1, n + 1):
        reg_no = f"REG{1000 + i}"
        name = fake.name()
        dept = random.choice(DEPARTMENTS)
        issued = datetime.now() - timedelta(days=random.randint(30, 700))
        expiry = issued + timedelta(days=365)
        # Deliberately make ~20% expired/inactive to exercise the
        # non-compliance branch of the workflow.
        status = "ACTIVE"
        if random.random() < 0.2:
            status = "EXPIRED"
            expiry = datetime.now() - timedelta(days=random.randint(1, 60))
        rows.append({
            "reg_no": reg_no,
            "name": name,
            "department": dept,
            "card_issued": issued.strftime("%Y-%m-%d"),
            "card_expiry": expiry.strftime("%Y-%m-%d"),
            "library_status": status,
        })

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"[dummy_data_generator] Wrote {len(rows)} library profiles -> {out_path}")
    return rows


def generate_sample_id_cards(profiles, out_dir=None, mismatch_ratio=0.15):
    """
    Draws simple synthetic ID card images for a subset of profiles.
    A `mismatch_ratio` of cards get a reg_no NOT present in the library
    DB, to simulate a student trying to gate-crash with an invalid card.
    """
    out_dir = out_dir or CARDS_DIR
    os.makedirs(out_dir, exist_ok=True)

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
        font_small = ImageFont.truetype("DejaVuSans.ttf", 16)
    except IOError:
        font = ImageFont.load_default()
        font_small = font

    for p in profiles:
        reg_no = p["reg_no"]
        if random.random() < mismatch_ratio:
            reg_no = f"REG{random.randint(9000, 9999)}"  # not in DB -> flagged

        img = Image.new("RGB", (400, 250), color=(235, 240, 245))
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 399, 40], fill=(30, 60, 120))
        draw.text((15, 8), "UNIVERSITY ID CARD", fill="white", font=font)
        draw.text((15, 60), f"Name: {p['name']}", fill="black", font=font_small)
        draw.text((15, 90), f"Reg No: {reg_no}", fill="black", font=font_small)
        draw.text((15, 120), f"Dept: {p['department']}", fill="black", font=font_small)
        draw.rectangle([280, 60, 380, 160], outline=(100, 100, 100))  # photo placeholder
        draw.text((295, 100), "PHOTO", fill=(150, 150, 150), font=font_small)

        fname = os.path.join(out_dir, f"{p['reg_no']}_card.png")
        img.save(fname)

    print(f"[dummy_data_generator] Wrote {len(profiles)} sample ID card images -> {out_dir}")


if __name__ == "__main__":
    profiles = generate_library_profiles(n=25)
    generate_sample_id_cards(profiles)
