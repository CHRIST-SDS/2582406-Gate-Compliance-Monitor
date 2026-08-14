"""
Generates docs/workflow.png — step-by-step runtime workflow.
Run once locally: python make_workflow.py
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

steps = [
    "1. Camera captures\nframe at gate",
    "2. YOLOv8 detects\nID card region",
    "3. OCR reads\nReg. No. / Name",
    "4. Lookup against\nLibrary Profile DB",
    "5a. Compliant →\nlog entry, no alert",
    "5b. Non-compliant →\ntrigger LLM + SD",
    "6. Ollama LLM writes\nincident report text",
    "7. Stable Diffusion\ngenerates alert visual",
    "8. Report + visual\nsaved to outputs/",
]

fig, ax = plt.subplots(figsize=(13, 8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 11)
ax.axis("off")
ax.text(5, 10.6, "Runtime Workflow — Gate Compliance Monitor", ha="center",
        fontsize=15, weight="bold", color="#1a1a1a")

colors = ["#233043"] * 4 + ["#1f3a2b", "#3a2b1f", "#1f3a2b", "#3a1f2f", "#232323"]

y = 9.4
for i, (step, color) in enumerate(zip(steps, colors)):
    b = FancyBboxPatch((2.2, y - 0.55), 5.6, 0.9, boxstyle="round,pad=0.08,rounding_size=0.1",
                        linewidth=1.6, edgecolor="#4a90e2", facecolor=color)
    ax.add_patch(b)
    ax.text(5, y - 0.1, step, ha="center", va="center", color="white", fontsize=10, weight="bold")
    if i < len(steps) - 1:
        arr = FancyArrowPatch((5, y - 0.55), (5, y - 1.05), arrowstyle="-|>",
                               mutation_scale=16, linewidth=1.6, color="#8fa3bf")
        ax.add_patch(arr)
    y -= 1.15

plt.tight_layout()
plt.savefig("workflow.png", dpi=150, facecolor="white")
print("Saved workflow.png")
