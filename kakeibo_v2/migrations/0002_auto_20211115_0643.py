# Generated by Django 3.2.3 on 2021-11-14 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kakeibo_v2', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cronkakeibo',
            name='card',
            field=models.CharField(blank=True, choices=[('SFC', 'SFC'), ('SFC（家族）', 'SFC（家族）'), ('GoldPoint', 'GoldPoint'), ('ANA USA', 'ANA USA')], max_length=255, null=True, verbose_name='カード'),
        ),
        migrations.AddField(
            model_name='kakeibo',
            name='card',
            field=models.CharField(blank=True, choices=[('SFC', 'SFC'), ('SFC（家族）', 'SFC（家族）'), ('GoldPoint', 'GoldPoint'), ('ANA USA', 'ANA USA')], max_length=255, null=True, verbose_name='カード'),
        ),
        migrations.AlterField(
            model_name='exchange',
            name='method',
            field=models.CharField(choices=[('Wise', 'Wise'), ('prestia', 'prestia'), ('その他', 'その他')], max_length=255, verbose_name='Method'),
        ),
    ]
