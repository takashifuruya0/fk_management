# Generated by Django 3.2.3 on 2021-07-07 01:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_currentuser.db.models.fields
import django_currentuser.middleware


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('kakeibo', '0005_resource_currency'),
    ]

    operations = [
        migrations.CreateModel(
            name='Exchange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('last_updated_at', models.DateTimeField(auto_now=True, verbose_name='最終更新日時')),
                ('is_active', models.BooleanField(default=True, verbose_name='有効')),
                ('legacy_id', models.IntegerField(blank=True, null=True, verbose_name='旧ID')),
                ('date', models.DateField(verbose_name='Date')),
                ('method', models.CharField(max_length=255, verbose_name='Method')),
                ('rate', models.FloatField(verbose_name='Rate (JPY)')),
                ('commission', models.FloatField(verbose_name='Commission')),
                ('currency', models.CharField(choices=[('JPY', 'JPY'), ('USD', 'USD')], max_length=3, verbose_name='Currency of commission')),
                ('created_by', django_currentuser.db.models.fields.CurrentUserField(blank=True, default=django_currentuser.middleware.get_current_authenticated_user, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='kakeibo_exchange_created_by', to=settings.AUTH_USER_MODEL, verbose_name='作成者')),
                ('kakeibo_from', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='exchange_from', to='kakeibo.kakeibo', verbose_name='Kakeibo_From')),
                ('kakeibo_to', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='exchange_to', to='kakeibo.kakeibo', verbose_name='Kakeibo_To')),
                ('last_updated_by', django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.CASCADE, on_update=True, related_name='kakeibo_exchange_last_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='最終更新者')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]