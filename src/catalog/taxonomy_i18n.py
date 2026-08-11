"""UK → EN назви довідників каталогу (імпорт / seed / backfill)."""

from __future__ import annotations

from typing import Iterable

from django.db.models import Q

from src.catalog.models import Composer, Format, Genre, Instrument, Level

# Ключі — нормалізовані name_uk (casefold після strip/collapse whitespace).
INSTRUMENT_EN: dict[str, str] = {
    'фортепіано': 'Piano',
    'фортепиано': 'Piano',
    'piano': 'Piano',
    'скрипка': 'Violin',
    'альт': 'Viola',
    'віолончель': 'Cello',
    'виолончель': 'Cello',
    'контрабас': 'Double bass',
    'флейта': 'Flute',
    'гобой': 'Oboe',
    'кларнет': 'Clarinet',
    'фагот': 'Bassoon',
    'саксофон': 'Saxophone',
    'труба': 'Trumpet',
    'тромбон': 'Trombone',
    'валторна': 'French horn',
    'туба': 'Tuba',
    'гітара': 'Guitar',
    'гитара': 'Guitar',
    'укулеле': 'Ukulele',
    'арфа': 'Harp',
    'орган': 'Organ',
    'акордеон': 'Accordion',
    'баян': 'Bayan',
    'ударні': 'Percussion',
    'барабани': 'Drums',
    'голос': 'Voice',
    'вокал': 'Voice',
    'хор': 'Choir',
    'ансамбль': 'Ensemble',
    'оркестр': 'Orchestra',
    'камерний ансамбль': 'Chamber ensemble',
}

GENRE_EN: dict[str, str] = {
    'класика': 'Classical',
    'класична': 'Classical',
    'романтика': 'Romantic',
    'романтизм': 'Romantic',
    'бароко': 'Baroque',
    'ренесанс': 'Renaissance',
    'модерн': 'Modern',
    'сучасна': 'Contemporary',
    'сучасність': 'Contemporary',
    'джаз': 'Jazz',
    'блюз': 'Blues',
    'поп': 'Pop',
    'рок': 'Rock',
    'фольк': 'Folk',
    'народна': 'Folk',
    'саундтрек': 'Soundtrack',
    'кіно': 'Film music',
    'духовна': 'Sacred',
    'літургійна': 'Liturgical',
    'опера': 'Opera',
    'оперета': 'Operetta',
    'мюзикл': 'Musical',
    'етюди': 'Etudes',
    'сонати': 'Sonatas',
    'концерти': 'Concertos',
    'симфонії': 'Symphonies',
    'камерна': 'Chamber',
    'дитяча': 'Children',
    'педагогіка': 'Educational',
}

LEVEL_EN: dict[str, str] = {
    'початківець': 'Beginner',
    'початковий': 'Beginner',
    'для початківців': 'Beginner',
    'легкий': 'Easy',
    'середній': 'Intermediate',
    'середній рівень': 'Intermediate',
    'просунутий': 'Advanced',
    'складний': 'Advanced',
    'професійний': 'Professional',
    'віртуозний': 'Virtuoso',
}

FORMAT_EN: dict[str, str] = {
    'зошит': 'Booklet',
    'збірник': 'Collection',
    'ноти': 'Sheet music',
    'партія': 'Part',
    'партітура': 'Score',
    'клавір': 'Piano reduction',
    'цифровий': 'Digital',
    'pdf': 'PDF',
    'книга': 'Book',
    'альбом': 'Album',
}

COMPOSER_EN: dict[str, str] = {
    'й. с. бах': 'J. S. Bach',
    'й.с. бах': 'J. S. Bach',
    'бах': 'Bach',
    'ф. шопен': 'F. Chopin',
    'шопен': 'Chopin',
    'п. і. чайковський': 'P. I. Tchaikovsky',
    'п.и. чайковский': 'P. I. Tchaikovsky',
    'чайковський': 'Tchaikovsky',
    'л. ван бетховен': 'L. van Beethoven',
    'бетховен': 'Beethoven',
    'м. клементі': 'M. Clementi',
    'клементі': 'Clementi',
    'р. шуман': 'R. Schumann',
    'шуман': 'Schumann',
    'в. а. моцарт': 'W. A. Mozart',
    'моцарт': 'Mozart',
    'ф. шуберт': 'F. Schubert',
    'шуберт': 'Schubert',
    'й. брамс': 'J. Brahms',
    'брамс': 'Brahms',
    'с. рахманінов': 'S. Rachmaninoff',
    'рахманінов': 'Rachmaninoff',
    'с. прокоф\'єв': 'S. Prokofiev',
    'прокоф\'єв': 'Prokofiev',
    'д. шостакович': 'D. Shostakovich',
    'шостакович': 'Shostakovich',
    'к. дебюссі': 'C. Debussy',
    'дебюссі': 'Debussy',
    'м. равель': 'M. Ravel',
    'равель': 'Ravel',
    'ф. ліст': 'F. Liszt',
    'ліст': 'Liszt',
    'н. паганіні': 'N. Paganini',
    'паганіні': 'Paganini',
    'а. вівальді': 'A. Vivaldi',
    'вівальді': 'Vivaldi',
    'г. ф. гендель': 'G. F. Handel',
    'гендель': 'Handel',
    'й. гайдн': 'J. Haydn',
    'гайдн': 'Haydn',
    'р. вагнер': 'R. Wagner',
    'вагнер': 'Wagner',
    'дж. верді': 'G. Verdi',
    'верді': 'Verdi',
    'п. і. чаиковский': 'P. I. Tchaikovsky',
}

_MODEL_MAPS: dict[type, dict[str, str]] = {
    Instrument: INSTRUMENT_EN,
    Genre: GENRE_EN,
    Level: LEVEL_EN,
    Format: FORMAT_EN,
    Composer: COMPOSER_EN,
}

TAXONOMY_MODELS: tuple[type, ...] = (
    Instrument,
    Genre,
    Level,
    Format,
    Composer,
)


def norm_name(name: str) -> str:
    return ' '.join((name or '').split()).strip()


def lookup_english(model: type, name_uk: str) -> str:
    """Повернути EN для UK-назви довідника або '' якщо немає в словнику."""
    key = norm_name(name_uk).casefold()
    if not key:
        return ''
    mapping = _MODEL_MAPS.get(model) or {}
    return mapping.get(key, '')


def ensure_english_name(obj, *, force: bool = False) -> bool:
    """
    Заповнити ``name_en`` зі словника.
    Повертає True, якщо поле змінено.
    """
    if obj is None:
        return False
    current = (getattr(obj, 'name_en', None) or '').strip()
    if current and not force:
        return False
    en = lookup_english(obj.__class__, getattr(obj, 'name_uk', '') or '')
    if not en or en == current:
        return False
    obj.name_en = en
    obj.save(update_fields=['name_en', 'updated_at'])
    return True


def fill_taxonomy_english(
    *,
    models: Iterable[type] | None = None,
    force: bool = False,
) -> dict[str, int]:
    """Backfill ``name_en`` для довідників. Повертає лічильники оновлень."""
    stats: dict[str, int] = {}
    for model in models or TAXONOMY_MODELS:
        updated = 0
        qs = model.objects.all()
        if not force:
            qs = qs.filter(Q(name_en='') | Q(name_en__isnull=True))
        for obj in qs.iterator():
            if ensure_english_name(obj, force=force):
                updated += 1
        stats[model.__name__] = updated
    return stats
