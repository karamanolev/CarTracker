# Generated by Django 2.0 on 2017-12-27 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobile_bg', '0018_mobilebgscrapelink_last_update_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='mobilebgadupdate',
            name='registration_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]