# Generated by Django 3.2.3 on 2021-10-18 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kakeibo', '0008_auto_20210829_2000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kakeibo',
            name='fee',
            field=models.FloatField(verbose_name='金額'),
        ),
    ]