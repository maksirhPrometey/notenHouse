"""Language switch that works with prefix_default_language=False."""

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import translate_url
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import (
    activate,
    check_for_language,
    get_language,
    get_language_from_path,
)
from django.views.i18n import LANGUAGE_QUERY_PARAMETER
from urllib.parse import urlsplit


def set_language(request):
    """
    Like django.views.i18n.set_language, but can translate /en/... URLs
    back to the default language when prefix_default_language=False.

    LocaleMiddleware forces LANGUAGE_CODE on unprefixed paths (e.g. /i18n/setlang/),
    so resolve('/en/...') fails and stock translate_url leaves next unchanged.
    """
    next_url = request.POST.get('next', request.GET.get('next'))
    if (
        next_url or request.accepts('text/html')
    ) and not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = request.META.get('HTTP_REFERER')
        if not url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            next_url = '/'

    response = HttpResponseRedirect(next_url) if next_url else HttpResponse(status=204)

    if request.method != 'POST':
        return response

    lang_code = request.POST.get(LANGUAGE_QUERY_PARAMETER)
    if not (lang_code and check_for_language(lang_code)):
        return response

    if next_url:
        path = urlsplit(next_url).path
        path_lang = get_language_from_path(path)
        previous = get_language()
        if path_lang:
            activate(path_lang)
        try:
            next_trans = translate_url(next_url, lang_code)
        finally:
            activate(previous)
        if next_trans != next_url:
            response = HttpResponseRedirect(next_trans)

    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        lang_code,
        max_age=settings.LANGUAGE_COOKIE_AGE,
        path=settings.LANGUAGE_COOKIE_PATH,
        domain=settings.LANGUAGE_COOKIE_DOMAIN,
        secure=settings.LANGUAGE_COOKIE_SECURE,
        httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
        samesite=settings.LANGUAGE_COOKIE_SAMESITE,
    )
    return response
