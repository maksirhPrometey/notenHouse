"""Content pages + contacts AJAX."""

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, TemplateView

from src.content.models import AboutPageSettings, SiteSettings
from src.content.site_blocks import get_block_text
from src.notifications.services import notify_lead_created_admin

from .contacts_defaults import merge_contacts
from .forms import ContactLeadForm
from .models import ContactLead, ContactTopic, Page


def _locale(request) -> str:
    return getattr(request, 'LANGUAGE_CODE', 'uk') or 'uk'


class PageDetailView(DetailView):
    template_name = 'content/page.html'
    context_object_name = 'page'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Page.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        page = self.object
        ctx['page_title'] = page.title_for(_locale(self.request))
        body = page.body_for(_locale(self.request))
        ctx['meta_description'] = (page.seo_description or body)[:160]
        return ctx


class ContactsView(TemplateView):
    template_name = 'content/contacts.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        site = SiteSettings.load()
        contacts = merge_contacts(site.contacts_json)
        locale = _locale(self.request)
        ctx.update(
            {
                'page_title': get_block_text('contacts', 'title', locale=locale),
                'meta_description': get_block_text(
                    'contacts', 'meta_description', locale=locale,
                ),
                'contacts': contacts,
                'schedule': contacts.get('schedule') or {},
                'form': ContactLeadForm(
                    initial={'topic': ContactTopic.ORDER},
                    locale=locale,
                ),
                'breadcrumbs': [
                    ('Home' if locale == 'en' else 'Головна', reverse('core:home')),
                    (get_block_text('contacts', 'title', locale=locale), None),
                ],
            }
        )
        return ctx


class ShippingPaymentView(TemplateView):
    template_name = 'content/shipping.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        site = SiteSettings.load()
        contacts = merge_contacts(site.contacts_json)
        show_pickup = bool(site.shipping_show_pickup)
        show_cod = bool(site.shipping_show_payment_cod)
        show_iban = bool(site.shipping_show_payment_iban)
        payment_count = 1 + int(show_cod) + int(show_iban)
        delivery_count = 2 + int(show_pickup)
        locale = _locale(self.request)
        page_title = get_block_text('shipping', 'title', locale=locale)
        meta = get_block_text('shipping', 'meta_description', locale=locale)
        ctx.update(
            {
                'page_title': page_title,
                'meta_description': meta[:160],
                'contacts': contacts,
                'show_pickup': show_pickup,
                'show_payment_cod': show_cod,
                'show_payment_iban': show_iban,
                'delivery_cols': delivery_count,
                'payment_cols': payment_count,
                'breadcrumbs': [
                    ('Home' if locale == 'en' else 'Головна', reverse('core:home')),
                    (page_title, None),
                ],
            }
        )
        return ctx


class AboutView(TemplateView):
    template_name = 'content/about.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        about = AboutPageSettings.load()
        locale = _locale(self.request)
        milestones = list(about.active_milestones())
        timeline = list(about.active_timeline())
        values = list(about.active_values())
        meta = (about.meta_description_for(locale) or about.hero_subtitle_for(locale) or '')[:160]
        home_label = 'Home' if locale == 'en' else 'Головна'
        about_label = 'About' if locale == 'en' else 'Про нас'
        ctx.update(
            {
                'page_title': about_label,
                'meta_description': meta,
                'about': about,
                'milestones': milestones,
                'timeline': timeline,
                'values': values,
                'milestones_cols': min(len(milestones), 4) or 1,
                'values_cols': min(len(values), 3) or 1,
                'breadcrumbs': [
                    (home_label, reverse('core:home')),
                    (about_label, None),
                ],
            }
        )
        return ctx


class ContactLeadCreateView(View):
    def post(self, request):
        locale = _locale(request)
        form = ContactLeadForm(request.POST, locale=locale)
        if not form.is_valid():
            return JsonResponse(
                {'ok': False, 'errors': form.errors},
                status=400,
            )
        data = form.cleaned_data
        lead = ContactLead.objects.create(
            name=data.get('name') or '',
            phone=data['phone'],
            email=data.get('email') or '',
            topic=data.get('topic') or '',
            message=data.get('message') or '',
            page_url=request.META.get('HTTP_REFERER', '')[:512],
        )
        notify_lead_created_admin(lead)
        locale = _locale(request)
        return JsonResponse(
            {
                'ok': True,
                'message': get_block_text('contacts', 'success', locale=locale),
            }
        )


def page_by_fixed_slug(slug: str):
    class FixedPageView(PageDetailView):
        def get_object(self, queryset=None):
            return get_object_or_404(Page, slug=slug, is_published=True)

    return FixedPageView
