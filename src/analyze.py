"""
Анализ результатов синтетической олимпиады.

Загружает данные из data/participants.csv, считает агрегаты
по регионам, гендеру, типу семьи и сохраняет сводный отчёт.
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "participants.csv"
OUTPUT_DIR = ROOT / "output"


def load_data() -> pd.DataFrame:
    """Читает CSV с участниками."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Файл данных не найден: {DATA_PATH}\n"
            f"Сначала запусти: python src/generate_data.py"
        )
    return pd.read_csv(DATA_PATH, encoding="utf-8-sig")


def overall_summary(df: pd.DataFrame) -> dict:
    """Общая статистика по олимпиаде."""
    return {
        "total_participants": len(df),
        "total_finalists": int(df["passed_round_1"].sum()),
        "pass_rate_%": round(df["passed_round_1"].mean() * 100, 1),
        "mean_round_1": round(df["round_1_score"].mean(), 1),
        "median_round_1": round(df["round_1_score"].median(), 1),
        "std_round_1": round(df["round_1_score"].std(), 1),
        "mean_round_2_finalists": round(df["round_2_score"].mean(), 1),
    }


def by_region(df: pd.DataFrame) -> pd.DataFrame:
    """Агрегаты по регионам."""
    grouped = (
        df.groupby("region")
        .agg(
            participants=("participant_id", "count"),
            mean_score=("round_1_score", "mean"),
            median_score=("round_1_score", "median"),
            finalists=("passed_round_1", "sum"),
        )
        .round(1)
    )
    grouped["pass_rate_%"] = (
        (grouped["finalists"] / grouped["participants"] * 100).round(1)
    )
    return grouped.sort_values("mean_score", ascending=False)


def by_gender(df: pd.DataFrame) -> pd.DataFrame:
    """Сравнение по гендеру."""
    return (
        df.groupby("gender")
        .agg(
            participants=("participant_id", "count"),
            mean_score=("round_1_score", "mean"),
            finalists=("passed_round_1", "sum"),
            pass_rate=("passed_round_1", "mean"),
        )
        .round({"mean_score": 1, "pass_rate": 3})
    )


def by_family_type(df: pd.DataFrame) -> pd.DataFrame:
    """Сравнение по типу семьи — ключевой социальный срез."""
    return (
        df.groupby("family_type")
        .agg(
            participants=("participant_id", "count"),
            mean_score=("round_1_score", "mean"),
            median_score=("round_1_score", "median"),
            finalists=("passed_round_1", "sum"),
            pass_rate=("passed_round_1", "mean"),
        )
        .round({"mean_score": 1, "median_score": 1, "pass_rate": 3})
    )


def by_language(df: pd.DataFrame) -> pd.DataFrame:
    """Сравнение по языку обучения."""
    return (
        df.groupby("language")
        .agg(
            participants=("participant_id", "count"),
            mean_score=("round_1_score", "mean"),
            pass_rate=("passed_round_1", "mean"),
        )
        .round({"mean_score": 1, "pass_rate": 3})
    )


def print_section(title: str, content) -> None:
    """Аккуратный заголовок секции в консоли."""
    bar = "=" * 60
    print(f"\n{bar}\n  {title}\n{bar}")
    print(content)


def main():
    df = load_data()

    overall = overall_summary(df)
    region_stats = by_region(df)
    gender_stats = by_gender(df)
    family_stats = by_family_type(df)
    language_stats = by_language(df)

    print_section("ОБЩАЯ СТАТИСТИКА", pd.Series(overall).to_string())
    print_section("ТОП РЕГИОНОВ ПО СРЕДНЕМУ БАЛЛУ", region_stats.head(10))
    print_section("ПО ГЕНДЕРУ", gender_stats)
    print_section("ПО ТИПУ СЕМЬИ", family_stats)
    print_section("ПО ЯЗЫКУ ОБУЧЕНИЯ", language_stats)

    # Сохраняем сводный отчёт по регионам
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / "summary_by_region.csv"
    region_stats.to_csv(report_path, encoding="utf-8-sig")

    print(f"\nOK Отчёт сохранён: {report_path}")


if __name__ == "__main__":
    main()
