# Generated by Django 2.0 on 2017-12-27 09:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mobile_bg', '0016_auto_20171227_1122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mobilebgad',
            name='last_price_change',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='last_price_change_ads', to='mobile_bg.MobileBgAdUpdate'),
        ),
    ]