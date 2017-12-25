# Generated by Django 2.0 on 2017-12-22 10:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mobile_bg', '0009_auto_20171221_1458'),
    ]

    operations = [
        migrations.CreateModel(
            name='MobileBgAdImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.IntegerField()),
                ('image_small', models.FileField(upload_to='mobile_bg/images/small/')),
                ('image_big', models.FileField(upload_to='mobile_bg/images/big/')),
                ('ad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='mobile_bg.MobileBgAd')),
            ],
        ),
    ]