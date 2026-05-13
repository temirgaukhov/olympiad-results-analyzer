"""
Визуализации результатов синтетической олимпиады.

Строит 4 графика и сохраняет их в output/charts/:
1. Топ-10 регионов по среднему баллу
2. Распределение баллов по гендеру (boxplot)
3. Распределение баллов по типу семьи (сравнение)
4. Доля финалистов по классам
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


def chart_family_type(df: pd.DataFrame) -> None:
    """Ключевой социальный срез: полная vs неполная семья."""
    family_labels = {"full": "Полная семья", "single": "Неполная семья"}
    df_plot = df.assign(family_label=df["family_type"].map(family_labels))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # Слева — распределение баллов
    sns.violinplot(
        data=df_plot, x="family_label", y="round_1_score",
        hue="family_label", palette=["#06A77D", "#D62828"],
        ax=ax1, legend=False, inner="quartile",
    )
    ax1.set_title("Распределение баллов", fontsize=13)
    ax1.set_xlabel("")
    ax1.set_ylabel("Балл (1 тур)")
    ax1.set_ylim(0, 100)

    # Справа — доля прошедших в финал
    pass_rate = (
        df_plot.groupby("family_label")["passed_round_1"]
        .mean()
        .mul(100)
        .round(1)
    )
    bars = ax2.bar(
        pass_rate.index, pass_rate.values,
        color=["#06A77D", "#D62828"],
    )
    ax2.set_title("Доля прошедших в финал, %", fontsize=13)
    ax2.set_ylabel("Доля финалистов, %")
    ax2.set_ylim(0, max(pass_rate.values) * 1.3)

    for bar, value in zip(bars, pass_rate.values):
        ax2.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
            f"{value}%", ha="center", fontsize=11, fontweight="bold",
        )

    fig.suptitle("Социальный срез: влияние типа семьи на результаты",
                 fontsize=15, y=1.02)

    plt.tight_layout()
    out = CHARTS_DIR / "03_family_type.png"
    plt.savefig(out, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"OK {out.name}")


def chart_by_grade(df: pd.DataFrame) -> None:
    """Средний балл по классам."""
    grade_stats = (
        df.groupby("grade")
        .agg(mean_score=("round_1_score", "mean"),
             count=("participant_id", "count"))
        .round(1)
    )

    fig, ax1 = plt.subplots(figsize=(10, 5))
    color1, color2 = "#264653", "#E76F51"

    # Левая ось — средний балл
    ax1.set_xlabel("Класс")
    ax1.set_ylabel("Средний балл", color=color1)
    ax1.plot(
        grade_stats.index, grade_stats["mean_score"],
        marker="o", linewidth=2.5, markersize=8, color=color1,
        label="Средний балл",
    )
    ax1.tick_params(axis="y", labelcolor=color1)
    ax1.set_ylim(0, 100)

    # Правая ось — количество участников
    ax2 = ax1.twinx()
    ax2.set_ylabel("Количество участников", color=color2)
    ax2.bar(
        grade_stats.index, grade_stats["count"],
        alpha=0.25, color=color2, label="Участников",
    )
    ax2.tick_params(axis="y", labelcolor=color2)

    plt.title("Средний балл и количество участников по классам", fontsize=14, pad=15)
    fig.tight_layout()

    out = CHARTS_DIR / "04_by_grade.png"
    plt.savefig(out, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"OK {out.name}")


def main():
    df = load_data()
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Строим графики из {len(df):,} записей...\n")

    chart_top_regions(df)
    chart_gender_boxplot(df)
    chart_family_type(df)
    chart_by_grade(df)

    print(f"\nГотово. Графики в: {CHARTS_DIR}")


if __name__ == "__main__":
    main()
