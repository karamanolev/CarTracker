# Generated by Django 2.0 on 2017-12-21 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobile_bg', '0008_auto_20171221_1458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mobilebgadupdate',
            name='html_raw',
            field=models.TextField(null=True),
        ),
    ]
