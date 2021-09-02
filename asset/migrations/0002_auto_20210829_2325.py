# Generated by Django 3.2.3 on 2021-08-29 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ipo',
            name='result_buy',
        ),
        migrations.AddField(
            model_name='ipo',
            name='managing_underwriter',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='主幹証券会社'),
        ),
        migrations.AddField(
            model_name='ipo',
            name='num_comment',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='コメント数'),
        ),
    ]
