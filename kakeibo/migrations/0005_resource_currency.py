# Generated by Django 3.2.3 on 2021-07-04 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kakeibo', '0004_event_detail'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='currency',
            field=models.CharField(choices=[('JPY', 'JPY'), ('USD', 'USD')], default='JPY', max_length=3, verbose_name='通貨'),
        ),
    ]
