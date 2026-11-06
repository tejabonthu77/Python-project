from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from analysis import load_data

CHART_DIR = Path(__file__).parent / "static" / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)


def generate_charts():
    df = load_data()
    plt.figure(figsize=(8, 4.5))
    if not df.empty:
        averages = df.groupby("subject_name")["marks_obtained"].mean().sort_values(ascending=False)
        plt.bar(averages.index, averages.values)
        plt.ylim(bottom=0)
    else:
        plt.text(0.5, 0.5, "No marks data available", ha="center", va="center")
        plt.xticks([])
    plt.title("Average Marks by Subject")
    plt.xlabel("Subject")
    plt.ylabel("Average marks (out of subject maximum)")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "subject_averages.png", dpi=140)
    plt.close()

    plt.figure(figsize=(6, 4.5))
    if not df.empty:
        passed = df["marks_obtained"] >= df["pass_marks"]
        counts = [int(passed.sum()), int((~passed).sum())]
        plt.bar(["Pass", "Fail"], counts)
    else:
        plt.text(0.5, 0.5, "No marks data available", ha="center", va="center")
        plt.xticks([])
    plt.title("Pass / Fail Assessment Records")
    plt.xlabel("Result")
    plt.ylabel("Number of records")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "pass_fail.png", dpi=140)
    plt.close()

    plt.figure(figsize=(8, 4.5))
    if not df.empty:
        percentages = df["marks_obtained"] / df["max_marks"] * 100
        plt.hist(percentages, bins=8, edgecolor="black")
        plt.xlim(0, 100)
    else:
        plt.text(0.5, 0.5, "No marks data available", ha="center", va="center")
        plt.xticks([])
    plt.title("Distribution of Assessment Percentages")
    plt.xlabel("Percentage (%)")
    plt.ylabel("Number of assessment records")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "marks_distribution.png", dpi=140)
    plt.close()
