# Generated by Django 2.0 on 2017-12-13 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobile_bg', '0003_auto_20171213_1101'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mobilebgadupdate',
            old_name='name',
            new_name='model_name',
        ),
        migrations.AddField(
            model_name='mobilebgadupdate',
            name='model_mod',
            field=models.CharField(default='', max_length=128),
            preserve_default=False,
        ),
    ]
