from django.db import migrations

RESERVED_PAGE_SLUGS = ('pro-nas', 'dostavka-i-oplata')


def remove_reserved_page_stubs(apps, schema_editor):
    Page = apps.get_model('content', 'Page')
    Page.objects.filter(slug__in=RESERVED_PAGE_SLUGS).delete()


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0010_image_help_text_and_processing'),
    ]

    operations = [
        migrations.RunPython(remove_reserved_page_stubs, noop_reverse),
    ]
