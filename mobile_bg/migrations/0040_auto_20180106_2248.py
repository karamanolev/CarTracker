# Generated by Django 2.0.1 on 2018-01-06 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobile_bg', '0039_auto_20180106_2245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mobilebgadupdate',
            name='model_mod',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]