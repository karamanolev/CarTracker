# Generated by Django 2.0 on 2017-12-21 12:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mobile_bg', '0007_auto_20171221_1338'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mobilebgadupdate',
            old_name='html',
            new_name='html_raw',
        ),
        migrations.AddField(
            model_name='mobilebgadupdate',
            name='html_delta',
            field=models.BinaryField(null=True),
        ),
        migrations.AlterField(
            model_name='mobilebgadupdate',
            name='prev_update',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='next_update', to='mobile_bg.MobileBgAdUpdate'),
        ),
    ]