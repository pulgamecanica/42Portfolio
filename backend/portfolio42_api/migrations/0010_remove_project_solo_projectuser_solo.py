# Generated by Django 4.2.7 on 2023-12-17 04:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio42_api', '0009_remove_user_intra_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='solo',
        ),
        migrations.AddField(
            model_name='projectuser',
            name='solo',
            field=models.BooleanField(default=True),
        ),
    ]
