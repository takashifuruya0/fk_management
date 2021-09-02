# Generated by Django 3.2.3 on 2021-08-29 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kakeibo', '0007_auto_20210813_1046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sharedresource',
            name='kind',
            field=models.CharField(choices=[('貯金', '貯金'), ('返済', '返済'), ('引き出し', '引き出し')], max_length=255, verbose_name='種別'),
        ),
        migrations.AlterField(
            model_name='sharedresource',
            name='val_goal',
            field=models.IntegerField(help_text='「引き出し」の場合は、目標金額は0とする', verbose_name='目標金額'),
        ),
    ]
