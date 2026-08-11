"""Cabinet views — auth, profile, orders, wishlist (tables.md §10)."""

from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as AuthLoginView
from django.contrib.auth.views import LogoutView as AuthLogoutView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import DetailView, FormView, ListView, TemplateView

from src.catalog.models import Product
from src.content.models import SiteSettings

from .forms import CabinetAuthenticationForm, ProfileForm, RegisterForm
from .models import CustomerProfile
from .services import (
    ACTIVE_ORDER_STATUSES,
    infer_primary_instrument,
    loyalty_level,
    order_status_pill,
    recommended_products_for_user,
    register_user,
    reorder_to_cart,
    toggle_wishlist,
    user_orders_qs,
    wishlist_products_qs,
)


def _brand_site_name() -> str:
    """SiteSettings brand — auth views must not leak RequestSite host into logo."""
    return SiteSettings.load().site_name


def cabinet_breadcrumbs(*tail):
    crumbs = [('Головна', reverse('core:home'))]
    if not tail:
        crumbs.append(('Кабінет', None))
    else:
        crumbs.append(('Кабінет', reverse('cabinet:dashboard')))
        crumbs.extend(tail)
    return crumbs


class RegisterView(FormView):
    template_name = 'cabinet/register.html'
    form_class = RegisterForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('cabinet:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Реєстрація'
        return ctx

    def form_valid(self, form):
        user = register_user(
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password1'],
            display_name=form.cleaned_data['display_name'],
            phone=form.cleaned_data.get('phone', ''),
        )
        login(self.request, user)
        messages.success(self.request, 'Вітаємо! Акаунт створено.')
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return redirect(next_url)
        return redirect('cabinet:dashboard')


class CabinetLoginView(AuthLoginView):
    template_name = 'cabinet/login.html'
    authentication_form = CabinetAuthenticationForm
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Вхід'
        # Django LoginView sets site_name from get_current_site(); without
        # django.contrib.sites that becomes request.get_host() (e.g. 127.0.0.1:8002).
        ctx['site_name'] = _brand_site_name()
        return ctx


class CabinetLogoutView(AuthLogoutView):
    next_page = 'core:home'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['site_name'] = _brand_site_name()
        return ctx


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'cabinet/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        orders_qs = user_orders_qs(user)
        order_count = orders_qs.count()
        recent_orders = list(orders_qs[:5])
        for order in recent_orders:
            label, tone = order_status_pill(order)
            order.pill_label = label
            order.pill_tone = tone

        active_deliveries = orders_qs.filter(status__in=ACTIVE_ORDER_STATUSES).count()
        wishlist_count = user.wishlist_items.count()
        primary_instrument = infer_primary_instrument(user)
        recommendations, rec_instrument = recommended_products_for_user(user, limit=4)

        profile, _ = CustomerProfile.objects.get_or_create(user=user)
        display_name = profile.display_name or user.first_name or user.email

        ctx.update(
            {
                'page_title': 'Кабінет',
                'display_name': display_name,
                'recent_orders': recent_orders,
                'order_count': order_count,
                'active_deliveries': active_deliveries,
                'wishlist_count': wishlist_count,
                'loyalty': loyalty_level(order_count=order_count),
                'primary_instrument': primary_instrument,
                'recommendations': recommendations,
                'recommend_instrument': rec_instrument or primary_instrument,
                'breadcrumbs': cabinet_breadcrumbs(),
            }
        )
        return ctx


class ProfileView(LoginRequiredMixin, View):
    template_name = 'cabinet/profile.html'

    def get(self, request):
        profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
        profile_form = ProfileForm(instance=profile)
        password_form = PasswordChangeForm(user=request.user)
        return self._render(request, profile_form, password_form)

    def post(self, request):
        profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
        profile_form = ProfileForm(instance=profile)
        password_form = PasswordChangeForm(user=request.user)
        if 'save_profile' in request.POST:
            profile_form = ProfileForm(request.POST, instance=profile)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Дані профілю оновлено')
                return redirect('cabinet:profile')
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Пароль змінено')
                return redirect('cabinet:profile')
        return self._render(request, profile_form, password_form)

    def _render(self, request, profile_form, password_form):
        return render(
            request,
            self.template_name,
            {
                'page_title': 'Профіль',
                'profile_form': profile_form,
                'password_form': password_form,
                'breadcrumbs': cabinet_breadcrumbs(('Профіль', None)),
            },
        )


class OrderListView(LoginRequiredMixin, ListView):
    template_name = 'cabinet/orders.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        return user_orders_qs(self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        for order in ctx['orders']:
            label, tone = order_status_pill(order)
            order.pill_label = label
            order.pill_tone = tone
        ctx['page_title'] = 'Мої замовлення'
        ctx['breadcrumbs'] = cabinet_breadcrumbs(('Замовлення', None))
        return ctx


class OrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'cabinet/order_detail.html'
    context_object_name = 'order'

    def get_object(self, queryset=None):
        return get_object_or_404(
            user_orders_qs(self.request.user).prefetch_related('items__product'),
            number=self.kwargs['number'],
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        label, tone = order_status_pill(self.object)
        ctx['pill_label'] = label
        ctx['pill_tone'] = tone
        ctx['page_title'] = f'Замовлення {self.object.number}'
        ctx['breadcrumbs'] = cabinet_breadcrumbs(
            ('Замовлення', reverse('cabinet:orders')),
            (f'№{self.object.number}', None),
        )
        return ctx


class OrderReorderView(LoginRequiredMixin, View):
    def post(self, request, number):
        order = get_object_or_404(user_orders_qs(request.user), number=number)
        added, errors = reorder_to_cart(request, order)
        if added:
            messages.success(
                request,
                f'Додано до кошика: {added} поз.',
            )
        for err in errors[:3]:
            messages.warning(request, err)
        if not added and not errors:
            messages.info(request, 'Немає товарів для повторення')
        if added:
            return redirect('commerce:cart')
        return redirect('cabinet:order_detail', number=number)


class WishlistView(LoginRequiredMixin, ListView):
    template_name = 'cabinet/wishlist.html'
    context_object_name = 'products'

    def get_queryset(self):
        return wishlist_products_qs(self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Обране'
        ctx['breadcrumbs'] = cabinet_breadcrumbs(('Обране', None))
        return ctx


class WishlistToggleView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        added = toggle_wishlist(request.user, product)
        if request.htmx:
            return render(
                request,
                'cabinet/partials/wishlist_button.html',
                {
                    'product': product,
                    'is_wishlisted': added,
                    'wishlist_count': request.user.wishlist_items.count(),
                    'oob_wishlist_header': True,
                },
            )
        next_url = request.POST.get('next') or 'cabinet:wishlist'
        return redirect(next_url)
