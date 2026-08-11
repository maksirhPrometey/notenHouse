# Sitemap-coverage verify (2026-07-27)

| URL з карти | urls | View | Шаблон | Навігація | Статус |
|---|---|---|---|---|---|
| `/` | ✅ | ✅ | ✅ | logo | ✅ |
| `/katalog/` | ✅ | ✅ | ✅ | header/footer | ✅ |
| `/katalog/{slug}/` | ✅ | ✅ | ✅ | facet | ✅ |
| `/nota/{slug}/` | ✅ | ✅ | ✅ | catalog | ✅ |
| `/poshuk/` | ✅ | ✅ | ✅ | header | ✅ |
| `/pro-nas/` | ✅ | ✅ | ✅ | header/footer | ✅ |
| `/dostavka-i-oplata/` | ✅ | ✅ | ✅ | header/footer | ✅ |
| `/kontakty/` | ✅ | ✅ | ✅ | header/footer | ✅ |
| `/koshyk/` | ✅ | ✅ | ✅ | header | ✅ |
| `/oformlennya/` | ✅ | ✅ | ✅ | cart CTA | ✅ |
| `/dyakuyemo/` | ✅ | ✅ | ✅ | after pay | ✅ |
| `/oformlennya/oplata/?order=` | ✅ | ✅ | ✅ | retry | ✅ (404 якщо order не існує) |
| `/payments/callback/` | ✅ | ✅ | — | ні | ✅ |
| `/api/np/cities/` | ✅ | ✅ | — | checkout JS | ✅ |
| `/api/np/warehouses/` | ✅ | ✅ | — | checkout JS | ✅ |
| `/sitemap.xml` | ✅ | ✅ | — | ні | ✅ |
| `/robots.txt` | ✅ | ✅ | — | ні | ✅ |
| `/en/…` | ✅ | i18n_patterns | ✅ | switcher | ✅ |
| `/admin/` | ✅ | Django | ✅ | staff | ✅ |
| `/healthz/` | ✅ | ✅ | — | ні | ✅ |
| `/kabinet/` | ✅ | ✅ | ✅ | header/mobile | ✅ |
| `/kabinet/vkhid/` | ✅ | ✅ | ✅ | dashboard link | ✅ |
| `/kabinet/reyestratsiya/` | ✅ | ✅ | ✅ | login link | ✅ |
| `/kabinet/vykhid/` | ✅ | ✅ | — (POST) | cabinet nav | ✅ |
| `/kabinet/profil/` | ✅ | ✅ | ✅ | cabinet nav | ✅ |
| `/kabinet/zamovlennya/` | ✅ | ✅ | ✅ | cabinet nav | ✅ |
| `/kabinet/zamovlennya/{number}/` | ✅ | ✅ | ✅ | orders list | ✅ |
| `/obrane/` | ✅ | ✅ | ✅ | header/mobile | ✅ |
| `/obrane/toggle/{product_id}/` | ✅ | ✅ | partial | PDP/wishlist | ✅ |

Поза MVP: промокоди, відгуки. Кабінет + wishlist — M5 unlocked 2026-07-27 (tables.md §10).

Smoke: `seed_demo` + Client GET/POST — основні 200; lead AJAX 200; add→cart→checkout 302/200; register→login→wishlist toggle→checkout(user FK)→orders list/detail — див. нижче.
