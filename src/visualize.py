"""
Визуализации результатов синтетической олимпиады.

Строит 2 графика и сохраняет их в output/charts/:
1. Топ-10 регионов по среднему баллу
2. Распределение баллов по гендеру (boxplot)
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "participants.csv"
CHARTS_DIR = ROOT / "output" / "charts"

# Единый стиль
sns.set_theme(style="whitegrid", font_scale=1.0)
PALETTE = "viridis"


def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Нет данных: {DATA_PATH}. Запусти: python src/generate_data.py"
        )
    return pd.read_csv(DATA_PATH, encoding="utf-8-sig")


def chart_top_regions(df: pd.DataFrame) -> None:
    """Топ-10 регионов по среднему баллу первого тура."""
    top = (
        df.groupby("region")["round_1_score"]
        .mean()
        .sort_values(ascending=True)
        .tail(10)
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(top.index, top.values, color=sns.color_palette(PALETTE, 10))

    ax.set_title("Топ-10 регионов по среднему баллу (1 тур)", fontsize=14, pad=15)
    ax.set_xlabel("Средний балл")
    ax.set_ylabel("")
    ax.set_xlim(0, 100)

    for bar, value in zip(bars, top.values):
        ax.text(
            value + 1, bar.get_y() + bar.get_height() / 2,
            f"{value:.1f}", va="center", fontsize=9,
        )

    plt.tight_layout()
    out = CHARTS_DIR / "01_top_regions.png"
    plt.savefig(out, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"OK {out.name}")


def chart_gender_boxplot(df: pd.DataFrame) -> None:
    """Распределение баллов по гендеру."""
    fig, ax = plt.subplots(figsize=(8, 5))
    gender_labels = {"M": "Мужской", "F": "Женский"}
    df_plot = df.assign(gender_label=df["gender"].map(gender_labels))

    sns.boxplot(
        data=df_plot, x="gender_label", y="round_1_score",
        hue="gender_label", palette=["#2E86AB", "#E63946"],
        ax=ax, legend=False,
    )

    ax.set_title("Распределение баллов по гендеру", fontsize=14, pad=15)
    ax.set_xlabel("")
    ax.set_ylabel("Балл (1 тур)")
    ax.set_ylim(0, 100)

    plt.tight_layout()
    out = CHARTS_DIR / "02_gender_distribution.png"
    plt.savefig(out, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"OK {out.name}")


def main():
    df = load_data()
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Строим графики из {len(df):,} записей...\n")

    chart_top_regions(df)
    chart_gender_boxplot(df)

    print(f"\nГотово. Графики в: {CHARTS_DIR}")


if __name__ == "__main__":
    main()
