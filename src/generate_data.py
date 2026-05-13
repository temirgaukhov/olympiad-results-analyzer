"""
Генератор синтетических данных для имитации результатов
региональной школьной олимпиады.

Данные ПОЛНОСТЬЮ ВЫМЫШЛЕНЫ и не связаны с реальными участниками
каких-либо организаций. Используются исключительно для демонстрации
навыков обработки и анализа табличных данных.
"""

import random
from pathlib import Path

import numpy as np
import pandas as pd

# Воспроизводимость результата
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# Количество синтетических участников
N_PARTICIPANTS = 5000

# Регионы Казахстана (актуально на 2024+)
REGIONS = [
    "Абайская область",
    "Акмолинская область",
    "Актюбинская область",
    "Алматинская область",
    "Атырауская область",
    "Восточно-Казахстанская область",
    "Жамбылская область",
    "Жетысуская область",
    "Западно-Казахстанская область",
    "Карагандинская область",
    "Костанайская область",
    "Кызылординская область",
    "Мангистауская область",
    "Павлодарская область",
    "Северо-Казахстанская область",
    "Туркестанская область",
    "Улытауская область",
    "г. Алматы",
    "г. Астана",
    "г. Шымкент",
]

# Условные шаблоны районов и школ — для каждого региона генерируем
# одинаковую "карту" районов и школ, чтобы получить иерархию
# регион → район → школа (как в реальной работе с данными олимпиады).
DISTRICT_NAMES = [
    "Центральный",
    "Северный",
    "Южный",
    "Восточный",
    "Западный",
    "Заречный",
    "Сельский",
]
SCHOOLS_PER_DISTRICT = 5  # 7 районов × 5 школ = 35 школ на регион

# Имена (для синтетических участников). Состав смешанный, как в реальной школе РК.
KZ_MALE = [
    "Адильхан", "Айдар", "Алихан", "Алмат", "Арман", "Аян", "Бауыржан",
    "Бекжан", "Дамир", "Данияр", "Ерасыл", "Ержан", "Жаныбек", "Нурлан",
    "Олжас", "Рамазан", "Санжар", "Темирлан", "Тимур", "Шынгыс",
]
KZ_FEMALE = [
    "Айгерим", "Айдана", "Алина", "Алтынай", "Аружан", "Аяна", "Балжан",
    "Гульнара", "Дана", "Дария", "Динара", "Жансая", "Камила", "Малика",
    "Меруерт", "Наргиз", "Сабина", "Сауле", "Томирис", "Эльмира",
]
RU_MALE = [
    "Александр", "Андрей", "Артём", "Владислав", "Дмитрий", "Иван",
    "Кирилл", "Максим", "Михаил", "Никита",
]
RU_FEMALE = [
    "Анастасия", "Анна", "Дарья", "Екатерина", "Елена", "Ксения",
    "Мария", "Ольга", "Полина", "София",
]

KZ_LAST = [
    "Темирбеков", "Сериков", "Алиев", "Бекенов", "Жумабеков", "Кадыров",
    "Нурланов", "Абилов", "Тулегенов", "Сатпаев", "Касенов", "Маратов",
]
RU_LAST = [
    "Иванов", "Петров", "Смирнов", "Кузнецов", "Соколов", "Попов",
    "Лебедев", "Новиков", "Морозов", "Волков",
]


def make_name(language: str, gender: str) -> tuple[str, str]:
    """Подбирает имя и фамилию под язык и гендер."""
    if language == "kk":
        first = random.choice(KZ_MALE if gender == "M" else KZ_FEMALE)
        last = random.choice(KZ_LAST)
        # У женщин в казахском контексте фамилия может оканчиваться на -ова/-кызы.
        # Для простоты оставляем мужскую форму — это синтетика, а не паспорт.
    else:
        first = random.choice(RU_MALE if gender == "M" else RU_FEMALE)
        last = random.choice(RU_LAST)
        if gender == "F":
            last = last + "а"  # Иванов -> Иванова
    return first, last


def generate_participants(n: int = N_PARTICIPANTS) -> pd.DataFrame:
    """Создаёт DataFrame с n синтетическими участниками олимпиады."""
    rows = []

    for i in range(1, n + 1):
        gender = random.choices(["M", "F"], weights=[0.48, 0.52])[0]
        language = random.choices(["kk", "ru"], weights=[0.65, 0.35])[0]
        first_name, last_name = make_name(language, gender)

        region = random.choice(REGIONS)
        district = random.choice(DISTRICT_NAMES) + " район"
        # Намеренно добавляем "грязь" в часть значений (~3%) — лишние пробелы.
        # Это имитирует реальные данные из форм/Excel и даёт повод
        # использовать .str.strip() в ноутбуках.
        if random.random() < 0.03:
            district = " " + district + " "
        school_num = random.randint(1, SCHOOLS_PER_DISTRICT)
        school = f"Школа №{school_num}"

        # ~30% — неполные семьи (используем эту переменную в анализе)
        family_type = random.choices(
            ["full", "single"], weights=[0.70, 0.30]
        )[0]

        # Балл первого тура: нормальное распределение, среднее ~55, std ~15.
        # Для неполных семей среднее чуть ниже (отражает паттерн из реальной аналитики).
        base_mean = 55
        if family_type == "single":
            base_mean -= 6  # реалистичный gap

        round_1_score = np.random.normal(loc=base_mean, scale=15)
        round_1_score = float(np.clip(round_1_score, 0, 100))
        round_1_score = round(round_1_score, 1)

        rows.append({
            "participant_id": f"P{i:05d}",
            "first_name": first_name,
            "last_name": last_name,
            "gender": gender,
            "region": region,
            "district": district,
            "school": school,
            "language": language,
            "family_type": family_type,
            "round_1_score": round_1_score,
        })

    df = pd.DataFrame(rows)

    # Топ 20% по баллу первого тура проходят в финал
    threshold = df["round_1_score"].quantile(0.80)
    df["passed_round_1"] = df["round_1_score"] >= threshold

    # У финалистов — балл второго тура, у остальных NaN
    finalist_mean = 65
    df["round_2_score"] = np.where(
        df["passed_round_1"],
        np.clip(np.random.normal(finalist_mean, 12, size=len(df)), 0, 100),
        np.nan,
    )
    df["round_2_score"] = df["round_2_score"].round(1)

    # Итоговый статус
    df["status"] = np.where(
        df["passed_round_1"], "finalist", "eliminated"
    )

    return df


def main():
    """Генерирует данные и сохраняет в data/participants.csv."""
    df = generate_participants()

    output_dir = Path(__file__).resolve().parent.parent / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "participants.csv"

    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"OK Сгенерировано: {len(df):,} участников")
    print(f"   Файл: {output_path}")
    print(f"   Финалистов: {df['passed_round_1'].sum():,}")
    print(f"   Регионов: {df['region'].nunique()}")
    unique_schools = df.groupby(['region', 'district', 'school']).ngroups
    print(f'   Уникальных школ: {unique_schools:,}')
    print(f"   Средний балл 1 тура: {df['round_1_score'].mean():.1f}")


if __name__ == "__main__":
    main()
