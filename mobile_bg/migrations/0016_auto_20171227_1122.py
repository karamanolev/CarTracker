# Generated by Django 2.0 on 2017-12-27 09:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mobile_bg', '0015_mobilebgad_last_active_update'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mobilebgad',
            old_name='last_price_drop',
            new_name='last_price_change',
        ),
    ]
