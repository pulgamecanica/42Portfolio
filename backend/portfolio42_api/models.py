from datetime import date, datetime
from django.utils import timezone
from django.db import models
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import AbstractUser
import logging


class IntraBaseModel(models.Model):
    intra_id = models.IntegerField(unique=True, db_index=True)
    updated_at = models.DateTimeField(auto_created=True, auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"(intra id: ${self.intra_id}"

    def was_updated_today(self):
        return self.updated_at > date.yesterday()


# User model
class User(AbstractUser, IntraBaseModel):
    intra_username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=130)
    intra_url = models.CharField(max_length=200)
    image_url = models.CharField(max_length=800)
    is_admin = models.BooleanField(default=False)

    cursus = models.ManyToManyField('Cursus', through='CursusUser', related_name='users')

    REQUIRED_FIELDS = ["email", "intra_id", "first_name", "last_name", 'intra_url', 'username']
    USERNAME_FIELD = "intra_username"

    def __str__(self):
        return "@" + self.intra_username

    def update(user):
        u = User.objects.get(intra_id=user['id'])

        u.intra_username = user['login']
        u.first_name = user['first_name']
        u.last_name = user['last_name']
        u.email = user['email']
        u.intra_url = user['url']
        u.image_url = user['image']['link']

        u.save()

        logging.info(f"Refreshed user: {u.intra_username} (id: {u.id}, intra_id: {u.intra_id})")
        return u



# Cursus model
class Cursus(IntraBaseModel):
    name = models.CharField(max_length=50)
    kind = models.CharField(max_length=50)

    skills = models.ManyToManyField('Skill', through='CursusSkill', related_name='cursus')

    def update(cursus):
        c, created = Cursus.objects.get_or_create(intra_id=cursus['id'])
        
        c.name = cursus['name'][:50]
        c.kind = cursus['kind'][:50]
        c.save()

        if (created):
            logging.info(f"Created new cursus: {c.name} (id: {c.id}, intra_id: {c.intra_id})")
        else:
            logging.info(f"Refreshed cursus: {c.name} (id: {c.id}, intra_id: {c.intra_id})")
        logging.debug(f"Updated cursus ({c.id}) with: intra_id={c.intra_id}, name={c.name}, kind={c.kind}")
        return c


# Project model
class Project(IntraBaseModel):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=2000)
    exam = models.BooleanField(default=False)
    solo = models.BooleanField(default=True)

    users = models.ManyToManyField('User', through='ProjectUser', related_name='projects')
    cursus = models.ManyToManyField('cursus', through='ProjectCursus', related_name='projects')
    
    def __str__(self):
        return f"{self.name}:{self.intra_id}"

    def update(project):
        p, created = Project.objects.get_or_create(intra_id=project['id'])

        p.name = project['name'][:50]
        if (created):
            
            try:
                p.description = project['description']
            except:
                p.description = project['slug']

        p.exam = project['exam']
        p.solo = False # todo: REMOVE THIS
        p.save()

        if (created):
            logging.info(f"Created new project: {p.name} (id: {p.id}, intra_id: {p.intra_id})")
        else:
            logging.info(f"Refreshed project: {p.name} (id: {p.id}, intra_id: {p.intra_id})")
        logging.debug(f"Updated project ({p.id}) with: intra_id={p.intra_id}, desc={p.description}, exam={p.exam}")

        return p

# Skill model
class Skill(IntraBaseModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}:{self.intra_id}"

    def update(skill):
        s, created = Skill.objects.get_or_create(intra_id=skill['id'])
    
        s.name = skill['name'][:100]
        s.save()

        if (created):
            logging.info(f"Created new skill: {s.name} (id: {s.id}, intra_id: {s.intra_id})")
        else:
            logging.info(f"Refreshed skill: {s.name} (id: {s.id}, intra_id: {s.intra_id})")
        logging.debug(f"Updated skill ({s.id}) with: intra_id={s.intra_id}, name={s.name}")
        
        return s

## Relations
# These are supposed to link the rest of the models together
# In the update function, the first arg is expected to be a Model,
# and the second is expected to be in json format (dictionary)

# This is a project that a user has subscribed to
class ProjectUser(IntraBaseModel):
    id_user = models.ForeignKey('User', on_delete=models.CASCADE)
    id_project = models.ForeignKey('Project', on_delete=models.CASCADE)
    grade = models.IntegerField()
    finished = models.BooleanField(default=False)
    finished_at = models.DateTimeField()

    def update(user, projectuser):
        p = Project.objects.get(intra_id=projectuser['project']['id'])
        pu, created = ProjectUser.objects.get_or_create(intra_id=projectuser['id'],
                                                        id_user=user,
                                                        id_project=p,
                                                        defaults={'finished_at': datetime(1,1,1,0,0),
                                                                  'finished': False,
                                                                  'grade': 0})
        
        pu.finished = projectuser['validated?'] if projectuser['validated?'] is not None else False
        if pu.finished:
            d = timezone.make_aware(datetime.strptime(projectuser['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ'), timezone.utc)
            pu.finished_at = d
        pu.grade = projectuser['final_mark'] if projectuser['final_mark'] is not None else 0
        pu.save()
        
        if (created):
            logging.info(f"Created new cursususer: (user: {pu.id_user}, project: {pu.id_project})")
        else:
            logging.info(f"Refreshed cursususer: (user: {pu.id_user}, project: {pu.id_project})")

        return pu

# This is a cursus a user is enrolled in
class CursusUser(IntraBaseModel):
    id_user = models.ForeignKey('User', on_delete=models.CASCADE)
    id_cursus = models.ForeignKey('Cursus', on_delete=models.CASCADE)
    level = models.FloatField()
    begin_at = models.DateField()

    def update(user, cursususer):
        c = Cursus.objects.get(intra_id=cursususer['cursus']['id'])
        cu, created = CursusUser.objects.get_or_create(intra_id=cursususer['id'],
                                                    id_user=user,
                                                    id_cursus=c,
                                                    defaults={'level': cursususer['level'],
                                                                'begin_at': cursususer['begin_at'][:10]})
        cu.level = cursususer['level']
        cu.save()

        if (created):
            logging.info(f"Created new cursususer: (cursus_id: {cu.id_cursus}, user_id: {cu.id_user})")
        else:
            logging.info(f"Refreshed cursususer: (cursus_id: {cu.id_cursus}, user_id: {cu.id_user})")
        
        return cu

# Creates a relation between a project and a cursus, it relates which projects are in a cursus
class ProjectCursus(models.Model):
    id_cursus = models.ForeignKey('Cursus', on_delete=models.CASCADE)
    id_project = models.ForeignKey('Project', on_delete=models.CASCADE)

    def update(cursus, project):
        p = Project.objects.get(intra_id=project['id'])
        cp, created = ProjectCursus.objects.get_or_create(id_project=p, id_cursus=cursus)
        cp.save()

        if (created):
            logging.info(f"Created new projectcursus: (project_id: {cp.id_project}, cursus_id: {cp.id_cursus})")
        else:
            logging.info(f"Refreshed projectcursus: (project_id: {cp.id_project}, cursus_id: {cp.id_cursus})")
        return cp


# Creates a relation between a skill and a cursus, it relates which skills are part of a cursus
class CursusSkill(models.Model):
    id_cursus = models.ForeignKey('Cursus', on_delete=models.CASCADE)
    id_skill = models.ForeignKey('Skill', on_delete=models.CASCADE)

    cursus_users = models.ManyToManyField('CursusUser', through='CursusUserSkill', related_name='skills')

    def update(cursus, skill):
        s = Skill.objects.get(intra_id=skill['id'])
        cs, created = CursusSkill.objects.get_or_create(id_cursus=cursus, id_skill=s)
        cs.save()

        if (created):
            logging.info(f"Created new cursusSkill: (cursus_id: {cs.id_cursus}, skill_id: {cs.id_skill})")
        else:
            logging.info(f"Refreshed cursusSkill: (cursus_id: {cs.id_cursus}, skill_id: {cs.id_skill})")
        return cs

# Creates a relation between a cursus skill and a cursus user
class CursusUserSkill(models.Model):
    id_cursus_skill = models.ForeignKey('CursusSkill', on_delete=models.CASCADE)
    id_cursus_user = models.ForeignKey('CursusUser', on_delete=models.CASCADE)
    level = models.FloatField()

    def update(cursusUser, cuSkill):
        s = Skill.objects.get(intra_id=cuSkill['id'])
        cs = CursusSkill.objects.get(id_cursus=cursusUser.id_cursus, id_skill=s)
        cus, created = CursusUserSkill.objects.get_or_create(id_cursus_user=cursusUser,
                                                             id_cursus_skill=cs,
                                                             defaults={'level': cuSkill['level']})
        cus.level = cuSkill['level']
        cus.save()

        if (created):
            logging.info(f"Created new cursususer: (cursus: {cus.id_cursus_skill}, user: {cus.id_cursus_user})")
        else:
            logging.info(f"Refreshed cursususer: (cursus: {cus.id_cursus_skill}, user: {cus.id_cursus_user})")
        return cus
