"""Convert / downscale / crop uploaded CMS images to WebP."""

from __future__ import annotations

import io
from pathlib import Path

from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from PIL import Image, ImageOps

from .image_specs import FitMode, ImageSpec

WEBP_QUALITY = 82


def is_new_upload(file_field) -> bool:
    """True for fresh admin/API uploads (not yet committed to storage)."""
    if not file_field:
        return False
    if isinstance(file_field, UploadedFile):
        return True
    return getattr(file_field, '_committed', True) is False


def _open_image(uploaded: UploadedFile) -> Image.Image:
    uploaded.seek(0)
    image = Image.open(uploaded)
    image.load()
    if image.mode not in {'RGB', 'RGBA'}:
        image = image.convert('RGBA' if 'A' in image.getbands() else 'RGB')
    return image


def _needs_downscale(image: Image.Image, spec: ImageSpec) -> bool:
    w, h = image.size
    return (
        w > int(spec.width * spec.oversize_ratio)
        or h > int(spec.height * spec.oversize_ratio)
    )


def _fit_image(image: Image.Image, spec: ImageSpec) -> Image.Image:
    if not _needs_downscale(image, spec):
        return image
    size = (spec.width, spec.height)
    if spec.mode is FitMode.COVER:
        return ImageOps.fit(image, size, method=Image.Resampling.LANCZOS)
    # CONTAIN: shrink to fit inside the box, keep aspect ratio
    fitted = image.copy()
    fitted.thumbnail(size, Image.Resampling.LANCZOS)
    return fitted


def _to_webp_upload(
    image: Image.Image,
    *,
    stem: str,
    field_name=None,
    quality: int = WEBP_QUALITY,
) -> InMemoryUploadedFile:
    buffer = io.BytesIO()
    image.save(buffer, format='WEBP', quality=quality, method=4)
    buffer.seek(0)
    name = f'{stem or "image"}.webp'
    return InMemoryUploadedFile(
        file=buffer,
        field_name=field_name,
        name=name,
        content_type='image/webp',
        size=buffer.getbuffer().nbytes,
        charset=None,
    )


def convert_upload_to_webp(
    uploaded: UploadedFile,
    *,
    quality: int = WEBP_QUALITY,
    spec: ImageSpec | None = None,
) -> InMemoryUploadedFile:
    """Return a WebP upload; optionally crop/scale when significantly oversized."""
    image = _open_image(uploaded)
    if spec is not None:
        image = _fit_image(image, spec)
    stem = Path(getattr(uploaded, 'name', 'image') or 'image').stem or 'image'
    return _to_webp_upload(
        image,
        stem=stem,
        field_name=getattr(uploaded, 'field_name', None),
        quality=quality,
    )


def process_upload(uploaded: UploadedFile, spec: ImageSpec) -> InMemoryUploadedFile:
    """Downscale/crop (if needed) and convert to WebP per ImageSpec."""
    return convert_upload_to_webp(uploaded, spec=spec)


def maybe_process_field(instance, field_name: str, spec: ImageSpec) -> None:
    """If ``field_name`` holds a new upload, replace it with a processed WebP."""
    field = getattr(instance, field_name, None)
    if is_new_upload(field):
        setattr(instance, field_name, process_upload(field, spec))
