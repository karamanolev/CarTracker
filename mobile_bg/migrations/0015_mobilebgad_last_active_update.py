# Generated by Django 2.0 on 2017-12-27 09:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mobile_bg', '0014_mobilebgscrapelink'),
    ]

    operations = [
        migrations.AddField(
            model_name='mobilebgad',
            name='last_active_update',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='last_active_update_ads', to='mobile_bg.MobileBgAdUpdate'),
        ),
    ]