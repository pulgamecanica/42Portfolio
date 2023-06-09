# Generated by Django 4.2.1 on 2023-05-22 14:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio42_api', '0005_skill'),
    ]

    operations = [
        migrations.CreateModel(
            name='CursusSkill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_cursus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio42_api.cursus')),
                ('id_skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio42_api.skill')),
            ],
        ),
        migrations.CreateModel(
            name='CursusUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.FloatField()),
                ('intra_id', models.IntegerField(db_index=True, unique=True)),
                ('begin_at', models.DateField()),
                ('id_cursus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio42_api.cursus')),
                ('id_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_created=True, auto_now=True)),
                ('intra_id', models.IntegerField(db_index=True, unique=True)),
                ('grade', models.IntegerField()),
                ('finished', models.BooleanField(default=False)),
                ('finished_at', models.DateTimeField()),
                ('id_project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio42_api.project')),
                ('id_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectCursus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_cursus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio42_api.cursus')),
                ('id_project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio42_api.project')),
            ],
        ),
        migrations.CreateModel(
            name='CursusUserSkill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.FloatField()),
                ('id_cursus_skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio42_api.cursusskill')),
                ('id_cursus_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio42_api.cursususer')),
            ],
        ),
        migrations.AddField(
            model_name='cursususer',
            name='skills',
            field=models.ManyToManyField(through='portfolio42_api.CursusUserSkill', to='portfolio42_api.cursusskill'),
        ),
        migrations.AddField(
            model_name='cursus',
            name='skills',
            field=models.ManyToManyField(through='portfolio42_api.CursusSkill', to='portfolio42_api.skill'),
        ),
        migrations.AddField(
            model_name='cursus',
            name='users',
            field=models.ManyToManyField(through='portfolio42_api.CursusUser', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='project',
            name='cursus',
            field=models.ManyToManyField(through='portfolio42_api.ProjectCursus', to='portfolio42_api.cursus'),
        ),
        migrations.AddField(
            model_name='project',
            name='users',
            field=models.ManyToManyField(through='portfolio42_api.ProjectUser', to=settings.AUTH_USER_MODEL),
        ),
    ]
