from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0003_cart_page_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='activetheme',
            name='color_footer_bg_mid',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Hex #RRGGBB. Порожньо = дефолт з colors.css.',
                max_length=7,
                validators=[
                    django.core.validators.RegexValidator(
                        message='Колір має бути у форматі #RRGGBB або порожнім',
                        regex='^$|^#[0-9A-Fa-f]{6}$',
                    ),
                ],
                verbose_name='Футер: середина градієнта',
            ),
        ),
        migrations.AddField(
            model_name='activetheme',
            name='color_footer_bg_end',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Hex #RRGGBB. Порожньо = дефолт з colors.css.',
                max_length=7,
                validators=[
                    django.core.validators.RegexValidator(
                        message='Колір має бути у форматі #RRGGBB або порожнім',
                        regex='^$|^#[0-9A-Fa-f]{6}$',
                    ),
                ],
                verbose_name='Футер: кінець градієнта',
            ),
        ),
        migrations.AlterField(
            model_name='activetheme',
            name='color_footer_bg',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Hex #RRGGBB. Порожньо = дефолт з colors.css.',
                max_length=7,
                validators=[
                    django.core.validators.RegexValidator(
                        message='Колір має бути у форматі #RRGGBB або порожнім',
                        regex='^$|^#[0-9A-Fa-f]{6}$',
                    ),
                ],
                verbose_name='Футер: початок градієнта',
            ),
        ),
    ]
