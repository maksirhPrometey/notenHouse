"""Dark-readable CMS widgets (admin_cms_blocks_skill §5)."""

from __future__ import annotations

from django.contrib.admin.widgets import AdminTextareaWidget, AdminTextInputWidget

_SKIP_CLASSES = frozenset({
    'bg-white',
    'text-font-default-light',
    'border-base-200',
    'dark:bg-base-900',
    'dark:border-base-700',
    'dark:text-font-default-dark',
})
_FORCE_CLASSES = (
    'bg-base-900',
    'text-base-100',
    'border-base-700',
    'placeholder-base-400',
)


def cms_control_classes(base_classes: list[str] | tuple[str, ...] | str) -> str:
    if isinstance(base_classes, str):
        parts = base_classes.split()
    else:
        parts = list(base_classes)
    cleaned = [c for c in parts if c not in _SKIP_CLASSES]
    for cls in _FORCE_CLASSES:
        if cls not in cleaned:
            cleaned.append(cls)
    return ' '.join(cleaned)


class CmsAdminTextInputWidget(AdminTextInputWidget):
    def __init__(self, attrs=None):
        super().__init__(attrs)
        existing = self.attrs.get('class', '')
        self.attrs['class'] = cms_control_classes(existing)


class CmsAdminTextareaWidget(AdminTextareaWidget):
    def __init__(self, attrs=None):
        super().__init__(attrs)
        existing = self.attrs.get('class', '')
        self.attrs['class'] = cms_control_classes(existing)


def apply_readable_widget(widget) -> None:
    """Mutate Unfold text widgets for dark-readable values."""
    from django.forms.widgets import CheckboxInput, FileInput, Select

    if isinstance(widget, (CheckboxInput, Select, FileInput)):
        return
    name = widget.__class__.__name__
    if 'TinyMCE' in name:
        return
    classes = widget.attrs.get('class', '')
    widget.attrs['class'] = cms_control_classes(classes)
