# NotenHaus — URL → controllers (ecommerce_business_logic_skill)

Джерело: notenhausSitemap.pdf · tables.md v1.1 · 2026-07-27

| URL з карти | App.Controller | Дія |
|---|---|---|
| `/` | `core.HomeView` | popular + new selectors |
| `/katalog/` | `catalog.CatalogListView` | filter/sort/view grid\|list |
| `/katalog/{slug}/` | `catalog.CatalogFacetView` | instrument OR genre by slug |
| `/nota/{slug}/` | `catalog.ProductDetailView` | PDP + add to cart form |
| `/poshuk/?q=` | `catalog.SearchView` | name/sku search |
| `/pro-nas/` | `content.PageDetailView` | slug=pro-nas |
| `/dostavka-i-oplata/` | `content.PageDetailView` | slug=dostavka-i-oplata |
| `/kontakty/` | `content.ContactsView` + `ContactLeadCreateView` | AJAX lead → Resend |
| `/koshyk/` | `commerce.CartDetailView` | qty/remove HTMX |
| POST add/update/remove | `commerce.Cart*View` | services |
| `/oformlennya/` | `commerce.CheckoutView` | place_order + LiqPay redirect |
| `/dyakuyemo/` | `commerce.ThankYouView` | after paid |
| `/oformlennya/oplata/?order=` | `commerce.PaymentRetryView` | awaiting retry |
| `/payments/callback/` | `payments.LiqPayCallbackView` | webhook |
| `/api/np/cities/` | `shipping.CitiesView` | NP API |
| `/api/np/warehouses/` | `shipping.WarehousesView` | NP API |
| `/sitemap.xml` | `seo.SitemapView` | |
| `/robots.txt` | `seo.RobotsView` | |
| `/en/…` | `i18n_patterns` | prefix_default_language=False |
| `/admin/` | Django admin | staff |
| `/healthz/` | `core.healthz` | |
| `/kabinet/` | `cabinet.DashboardView` | login required |
| `/kabinet/vkhid/` | `cabinet.CabinetLoginView` | email+пароль |
| `/kabinet/reyestratsiya/` | `cabinet.RegisterView` | створює User+CustomerProfile |
| `/kabinet/vykhid/` | `cabinet.CabinetLogoutView` | POST-only |
| `/kabinet/profil/` | `cabinet.ProfileView` | профіль + зміна пароля |
| `/kabinet/zamovlennya/` | `cabinet.OrderListView` | user OR customer_email |
| `/kabinet/zamovlennya/<number>/` | `cabinet.OrderDetailView` | лише власник |
| `/obrane/` | `cabinet.WishlistView` | login required |
| POST `/obrane/toggle/<product_id>/` | `cabinet.WishlistToggleView` | HTMX toggle |

M5 unlocked (2026-07-27): кабінет + wishlist — див. tables.md §10. Поза MVP лишаються: промокоди, відгуки.
