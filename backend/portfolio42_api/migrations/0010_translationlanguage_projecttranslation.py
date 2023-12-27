# Generated by Django 4.2.7 on 2023-12-27 06:01

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio42_api', '0009_remove_user_intra_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='TranslationLanguage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_short', models.CharField(max_length=8, unique=True, validators=[django.core.validators.RegexValidator('([A-Z]+-[A-Z]+)|(default)')])),
                ('name_full', models.CharField(max_length=64, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_created=True, auto_now=True)),
                ('description', models.TextField(max_length=2000)),
                ('description_bonus', models.TextField(max_length=2000)),
                ('bonus_append', models.BooleanField(default=True)),
                ('id_language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio42_api.translationlanguage')),
                ('id_project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio42_api.project')),
            ],
        ),
    ]
