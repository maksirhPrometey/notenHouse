"""Ідемпотентний імпорт товарів (тисячі рядків, батчами)."""

from __future__ import annotations

import html
import logging
from pathlib import Path
from typing import BinaryIO, Iterator

from django.db import transaction
from django.utils import timezone
from django.utils.text import Truncator

from src.catalog.models import Genre, Instrument, Product, ProductImportJob

from .parsers_csv import iter_csv_rows
from .parsers_yml import iter_yml_rows
from .resolve import find_existing_product
from .row import ImportRow
from .slug_utils import unique_slug
from .taxonomy import (
    get_or_create_by_name,
    resolve_category,
    resolve_composer,
    resolve_format,
    resolve_level,
)

logger = logging.getLogger(__name__)

BATCH_SIZE = 100
MAX_REPORT_ERRORS = 50


def detect_format(filename: str, explicit: str = '') -> str:
    if explicit in {ProductImportJob.FileFormat.CSV, ProductImportJob.FileFormat.YML}:
        return explicit
    suffix = Path(filename or '').suffix.lower()
    if suffix == '.csv':
        return ProductImportJob.FileFormat.CSV
    if suffix in {'.yml', '.xml', '.yaml'}:
        return ProductImportJob.FileFormat.YML
    raise ValueError('Невідомий формат. Підтримуються .csv, .yml, .xml')


def iter_rows(stream: BinaryIO, fmt: str) -> Iterator[ImportRow]:
    if fmt == ProductImportJob.FileFormat.CSV:
        yield from iter_csv_rows(stream)
    elif fmt == ProductImportJob.FileFormat.YML:
        yield from iter_yml_rows(stream)
    else:
        raise ValueError(f'Невідомий формат: {fmt}')


def _clean_text(value: str) -> str:
    return html.unescape((value or '').strip())


def _ensure_sku(row: ImportRow, product: Product | None) -> str:
    sku = (row.sku or '').strip()
    if sku:
        return sku[:64]
    if product is not None:
        return product.sku
    if row.barcode:
        return f'BC-{row.barcode}'[:64]
    base = unique_slug(Product, row.name_uk or 'product')
    return f'NH-{base}'[:64]


def _collect_taxonomies(row: ImportRow, caches: dict) -> tuple[list, list, object, object, object]:
    composer = resolve_composer(row.composer, cache=caches['composer']) if row.composer else None
    level = resolve_level(row.level, cache=caches['level']) if row.level else None
    fmt = resolve_format(row.format_name, cache=caches['format']) if row.format_name else None

    instruments: list = []
    genres: list = []
    if row.category:
        cat_inst, cat_gen = resolve_category(
            row.category,
            instrument_cache=caches['instrument'],
            genre_cache=caches['genre'],
        )
        instruments.extend([x for x in cat_inst if x])
        genres.extend([x for x in cat_gen if x])
    for name in row.instruments:
        obj = get_or_create_by_name(Instrument, name, cache=caches['instrument'])
        if obj:
            instruments.append(obj)
    for name in row.genres:
        obj = get_or_create_by_name(Genre, name, cache=caches['genre'])
        if obj:
            genres.append(obj)
    return instruments, genres, composer, level, fmt


def _apply_row(row: ImportRow, *, caches: dict) -> str:
    name_uk = _clean_text(row.name_uk)
    if not name_uk:
        raise ValueError('Порожня назва')
    if row.price_uah is None:
        raise ValueError('Немає ціни')
    if row.price_uah < 0:
        raise ValueError('Ціна < 0')

    product = find_existing_product(row)
    sku = _ensure_sku(row, product)
    if product is None:
        product = Product.objects.filter(sku__iexact=sku).first()

    instruments, genres, composer, level, fmt = _collect_taxonomies(row, caches)
    stock = row.stock_qty if row.stock_qty is not None else (product.stock_qty if product else 0)
    barcode = (row.barcode or '').strip()

    defaults = {
        'name_uk': name_uk,
        'name_en': _clean_text(row.name_en) or (product.name_en if product else ''),
        'composer': composer if row.composer else (product.composer if product else None),
        'level': level if row.level else (product.level if product else None),
        'format': fmt if row.format_name else (product.format if product else None),
        'description_uk': _clean_text(row.description_uk) or (
            product.description_uk if product else ''
        ),
        'description_en': _clean_text(row.description_en) or (
            product.description_en if product else ''
        ),
        'price_uah': row.price_uah,
        'stock_qty': max(0, int(stock)),
        'is_published': True,
        'barcode': barcode if barcode else (product.barcode if product else ''),
    }

    if product is None:
        product = Product.objects.create(
            sku=sku,
            slug=unique_slug(Product, name_uk),
            published_at=timezone.now(),
            **defaults,
        )
        action = 'created'
    else:
        for key, value in defaults.items():
            setattr(product, key, value)
        if (row.sku or '').strip() and product.sku != sku:
            if not Product.objects.filter(sku__iexact=sku).exclude(pk=product.pk).exists():
                product.sku = sku
        if not product.published_at and product.is_published:
            product.published_at = timezone.now()
        product.save()
        action = 'updated'

    if instruments:
        product.instruments.set({i.pk for i in instruments})
    if genres:
        product.genres.set({g.pk for g in genres})
    return action


def _process_batch(
    rows: list[ImportRow],
    caches: dict,
) -> tuple[int, int, int, int, list[dict]]:
    created = updated = skipped = errors = 0
    samples: list[dict] = []
    with transaction.atomic():
        for row in rows:
            try:
                if not _clean_text(row.name_uk) and row.price_uah is None:
                    skipped += 1
                    continue
                action = _apply_row(row, caches=caches)
                if action == 'created':
                    created += 1
                else:
                    updated += 1
            except Exception as exc:
                errors += 1
                if len(samples) < MAX_REPORT_ERRORS:
                    samples.append({
                        'line': row.line_no,
                        'sku': row.sku,
                        'name': Truncator(row.name_uk or '').chars(80),
                        'error': str(exc)[:300],
                    })
    return created, updated, skipped, errors, samples


def run_product_import(job: ProductImportJob) -> ProductImportJob:
    job.status = ProductImportJob.Status.RUNNING
    job.started_at = timezone.now()
    job.error_message = ''
    job.save(update_fields=['status', 'started_at', 'error_message'])

    created = updated = skipped = errors = 0
    error_samples: list[dict] = []
    caches = {
        'composer': {},
        'instrument': {},
        'genre': {},
        'level': {},
        'format': {},
    }

    try:
        fmt = detect_format(job.file.name, job.format)
        job.format = fmt
        job.save(update_fields=['format'])

        with job.file.open('rb') as stream:
            batch: list[ImportRow] = []
            for row in iter_rows(stream, fmt):
                batch.append(row)
                if len(batch) < BATCH_SIZE:
                    continue
                c, u, s, e, samples = _process_batch(batch, caches)
                created += c
                updated += u
                skipped += s
                errors += e
                error_samples.extend(samples)
                batch = []
            if batch:
                c, u, s, e, samples = _process_batch(batch, caches)
                created += c
                updated += u
                skipped += s
                errors += e
                error_samples.extend(samples)

        job.created_count = created
        job.updated_count = updated
        job.skipped_count = skipped
        job.error_count = errors
        job.report_json = {
            'created': created,
            'updated': updated,
            'skipped': skipped,
            'errors': errors,
            'error_samples': error_samples[:MAX_REPORT_ERRORS],
        }
        job.status = ProductImportJob.Status.DONE
        job.finished_at = timezone.now()
        job.save()
    except Exception as exc:
        logger.exception('Product import failed job=%s', job.pk)
        job.status = ProductImportJob.Status.FAILED
        job.error_message = str(exc)[:2000]
        job.finished_at = timezone.now()
        job.created_count = created
        job.updated_count = updated
        job.skipped_count = skipped
        job.error_count = errors
        job.report_json = {
            'created': created,
            'updated': updated,
            'skipped': skipped,
            'errors': errors,
            'error_samples': error_samples[:MAX_REPORT_ERRORS],
        }
        job.save()

    return job
