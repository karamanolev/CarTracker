# Generated by Django 2.0.1 on 2018-01-18 19:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mobile_bg', '0049_auto_20180115_1501'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mobilebgad',
            name='topmenu',
        ),
    ]
