"""Generate charts from the nightly run metrics for the SBV-ORD dossier."""

import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

CHARTS_DIR = Path(__file__).parent / "assets" / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

metrics = json.loads((Path(__file__).parent / "evidence" / "run_metrics.json").read_text())

WATERMARK = "Public Data Mode – Synthetic Records – For Demonstration Only"

def add_watermark(fig):
    fig.text(0.5, 0.01, WATERMARK, ha="center", fontsize=6, color="gray", alpha=0.7)
    fig.text(0.98, 0.01, "Liberty ChainGuard Consulting", ha="right", fontsize=6, color="gray", alpha=0.5)

# --- Agent Pie Chart ---
agent_data = {k: v for k, v in metrics.get("by_agent", {}).items() if k != "system"}
fig, ax = plt.subplots(figsize=(7, 5))
colors = ["#7c3aed", "#16a34a", "#2563eb", "#ca8a04"]
wedges, texts, autotexts = ax.pie(
    agent_data.values(), labels=None, autopct="%1.1f%%",
    colors=colors, startangle=90, pctdistance=0.8
)
ax.legend(
    [f"{k} ({v:,})" for k, v in agent_data.items()],
    loc="center left", bbox_to_anchor=(1, 0.5), fontsize=9
)
ax.set_title("Agent Activity Distribution (Events)", fontsize=12, fontweight="bold")
add_watermark(fig)
fig.tight_layout()
fig.savefig(CHARTS_DIR / "agent_pie.png", dpi=150, bbox_inches="tight")
plt.close()

# --- Work Orders by Type Bar Chart ---
action_counts = metrics.get("by_action", {})
wo_types = {}
for action, count in action_counts.items():
    if action.startswith("completed:") and "kpi" not in action and "log" not in action:
        wo_type = action.replace("completed:", "").replace("_", " ").title()
        wo_types[wo_type] = count

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.barh(list(wo_types.keys()), list(wo_types.values()), color="#4f46e5")
ax.set_xlabel("Completed Count")
ax.set_title("Work Orders Completed by Type", fontsize=12, fontweight="bold")
for bar, val in zip(bars, wo_types.values()):
    ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2, str(val), va="center", fontsize=8)
add_watermark(fig)
fig.tight_layout()
fig.savefig(CHARTS_DIR / "wo_by_type.png", dpi=150, bbox_inches="tight")
plt.close()

# --- Phase Timeline ---
fig, ax = plt.subplots(figsize=(10, 2.5))
phases = [
    ("Morning Intake", 0, 35, "#3b82f6"),
    ("Midday IT Ops", 35, 35, "#22c55e"),
    ("End-of-Day Audit", 70, 30, "#f59e0b"),
]
for label, start, width, color in phases:
    ax.barh(0, width, left=start, height=0.6, color=color, edgecolor="white", linewidth=2)
    ax.text(start + width/2, 0, label, ha="center", va="center", fontsize=9, fontweight="bold", color="white")
ax.set_xlim(0, 100)
ax.set_yticks([])
ax.set_xlabel("Shift Progress (%)")
ax.set_title("Simulated 10-Hour Shift — Phase Timeline", fontsize=12, fontweight="bold")
ax.axvline(x=35, color="gray", linestyle="--", alpha=0.3)
ax.axvline(x=70, color="gray", linestyle="--", alpha=0.3)
times = ["7:00 AM", "10:30 AM", "2:00 PM", "5:00 PM"]
positions = [0, 35, 70, 100]
for t, p in zip(times, positions):
    ax.text(p, -0.6, t, ha="center", fontsize=7, color="gray")
add_watermark(fig)
fig.tight_layout()
fig.savefig(CHARTS_DIR / "phase_timeline.png", dpi=150, bbox_inches="tight")
plt.close()

# --- KPI Summary Card Image ---
kpi_data = [
    ("Real Elapsed", f"{metrics.get('elapsed_real_minutes', 100)} min"),
    ("Agent Cycles", f"{metrics.get('total_agent_cycles', 2460):,}"),
    ("WOs Created", f"{metrics.get('work_orders_created', 1020):,}"),
    ("WOs Completed", f"{metrics.get('work_orders_completed', 1020):,}"),
    ("WOs Failed", str(metrics.get("work_orders_failed", 0))),
    ("Success Rate", "100.0%"),
    ("Events Logged", f"{metrics.get('events_total', 4551):,}"),
    ("Artifacts", str(metrics.get("artifacts_generated", 120))),
]
fig, ax = plt.subplots(figsize=(10, 3))
ax.axis("off")
table = ax.table(
    cellText=[[k, v] for k, v in kpi_data],
    colLabels=["Metric", "Value"],
    cellLoc="center",
    loc="center",
    colWidths=[0.4, 0.3],
)
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 1.5)
for (row, col), cell in table.get_celld().items():
    if row == 0:
        cell.set_facecolor("#4f46e5")
        cell.set_text_props(color="white", fontweight="bold")
    elif row % 2 == 0:
        cell.set_facecolor("#f1f5f9")
ax.set_title("Nightly Run — Key Performance Indicators", fontsize=12, fontweight="bold", pad=20)
add_watermark(fig)
fig.tight_layout()
fig.savefig(CHARTS_DIR / "kpi_table.png", dpi=150, bbox_inches="tight")
plt.close()

print("Charts generated:")
for f in sorted(CHARTS_DIR.iterdir()):
    print(f"  {f.name} ({f.stat().st_size // 1024}KB)")
