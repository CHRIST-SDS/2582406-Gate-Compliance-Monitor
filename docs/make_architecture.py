"""
Generates docs/architecture.png — a clean block diagram of the
Gate Compliance Monitor pipeline. Run once locally: python make_architecture.py
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(13, 7))
ax.set_xlim(0, 13)
ax.set_ylim(0, 7)
ax.axis("off")

def box(x, y, w, h, text, color="#2b2f38", text_color="white", fontsize=10, edge="#4a90e2"):
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.08",
                        linewidth=1.6, edgecolor=edge, facecolor=color)
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            color=text_color, fontsize=fontsize, weight="bold", wrap=True)

def arrow(x1, y1, x2, y2, color="#8fa3bf"):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=16,
                         linewidth=1.6, color=color)
    ax.add_patch(a)

# Title
ax.text(6.5, 6.6, "AI-Powered Gate Compliance Monitor — Architecture",
        ha="center", fontsize=15, weight="bold", color="#1a1a1a")

# Row 1: Input
box(0.3, 5.2, 2.2, 0.9, "Entrance Gate\nCamera Feed", color="#1f2430")

# Detection
box(3.0, 5.2, 2.4, 0.9, "ID Card Detector\n(YOLOv8, local)", color="#233043")
arrow(2.5, 5.65, 3.0, 5.65)

# OCR
box(5.8, 5.2, 2.4, 0.9, "OCR Extraction\n(EasyOCR / Tesseract)", color="#233043")
arrow(5.4, 5.65, 5.8, 5.65)

# DB Sync
box(8.6, 5.2, 2.4, 0.9, "Library Profile DB\n(SQLite Sync)", color="#233043")
arrow(8.2, 5.65, 8.6, 5.65)

# Compliance Engine (center hub)
box(4.7, 3.3, 3.6, 1.0, "Compliance Engine\n(Rule-based match & decision)", color="#3a2b1f", edge="#e2a34a")
arrow(9.8, 5.2, 7.5, 4.3)
arrow(6.0, 5.2, 6.2, 4.3)

# Branch: Local LLM
box(1.2, 1.5, 3.0, 1.0, "Local LLM (Ollama)\nLlama 3 / Mistral\n→ Incident Report Text", color="#1f3a2b", edge="#4ae28f")
arrow(5.2, 3.3, 3.0, 2.5)

# Branch: Local Image Gen
box(8.8, 1.5, 3.0, 1.0, "Local Image Gen\nStable Diffusion (A1111/ComfyUI)\n→ Alert Visual", color="#3a1f2f", edge="#e24a8f")
arrow(7.8, 3.3, 9.8, 2.5)

# Output dashboard
box(4.7, 0.2, 3.6, 1.0, "Dashboard / Outputs\n(reports/, alerts/, logs)", color="#232323", edge="#cccccc")
arrow(2.7, 1.5, 5.5, 1.2)
arrow(10.3, 1.5, 7.5, 1.2)

plt.tight_layout()
plt.savefig("architecture.png", dpi=150, facecolor="white")
print("Saved architecture.png")
