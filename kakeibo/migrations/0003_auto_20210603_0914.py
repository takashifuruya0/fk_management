# Generated by Django 3.2.3 on 2021-06-03 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kakeibo', '0002_auto_20210529_1047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credit',
            name='memo',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='備考'),
        ),
        migrations.AlterField(
            model_name='cronkakeibo',
            name='memo',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='備考'),
        ),
        migrations.AlterField(
            model_name='event',
            name='memo',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='備考'),
        ),
        migrations.AlterField(
            model_name='kakeibo',
            name='memo',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='備考'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='memo',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='備考'),
        ),
        migrations.AlterField(
            model_name='sharedkakeibo',
            name='memo',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='備考'),
        ),
        migrations.AlterField(
            model_name='target',
            name='memo',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='備考'),
        ),
        migrations.AlterField(
            model_name='usage',
            name='memo',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='備考'),
        ),
        migrations.AlterField(
            model_name='way',
            name='memo',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='備考'),
        ),
    ]
