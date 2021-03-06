# Generated by Django 2.0.1 on 2018-01-12 14:32

from django.db import migrations, models
from django.utils import timezone


def _set_photo_object_at(apps, schema_editor):
    MobileBgAdImage = apps.get_model('mobile_bg', 'MobileBgAdImage')
    MobileBgAdImage.objects.filter(photo_object__isnull=False).update(photo_object_at=timezone.now())


class Migration(migrations.Migration):
    dependencies = [
        ('mobile_bg', '0044_mobilebgadimage_photo_object'),
    ]

    operations = [
        migrations.AddField(
            model_name='mobilebgadimage',
            name='photo_object_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.RunPython(_set_photo_object_at, migrations.RunPython.noop, elidable=True)
    ]
