# Generated by Django 4.2.3 on 2023-10-14 00:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio42_api', '0008_cursususer_updated_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='intra_username',
        ),
    ]