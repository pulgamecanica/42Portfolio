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

def log_update(t, is_created):
    logging.info(f"{'Created new' if is_created else 'Refreshed'} {type(t).__name__}: {t}")


# Basic models

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
        return f"({self.intra_username})"

    def update(user):
        try:
            u = User.objects.get(intra_id=user['id'])
        except:
            logging.error(f"Could not find User with (intra_id: {user['id']})")
            return None

        u.intra_username = user['login']
        u.first_name = user['first_name']
        u.last_name = user['last_name']
        u.email = user['email']
        u.intra_url = user['url']
        u.image_url = user['image']['link']

        u.save()

        log_update(u, False)
        return u



# Cursus model
class Cursus(IntraBaseModel):
    name = models.CharField(max_length=50)
    kind = models.CharField(max_length=50)

    skills = models.ManyToManyField('Skill', through='CursusSkill', related_name='cursus')

    def __str__(self):
        return f"({self.name})"

    def update(cursus):
        c, created = Cursus.objects.get_or_create(intra_id=cursus['id'])

        c.name = cursus['name'][:50]
        c.kind = cursus['kind'][:50]
        c.save()

        log_update(c, created)

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
        return f"({self.name})"

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

        log_update(p, created)

        return p

# Skill model
class Skill(IntraBaseModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"({self.name})"

    def update(skill):
        s, created = Skill.objects.get_or_create(intra_id=skill['id'])

        s.name = skill['name'][:100]
        s.save()

        log_update(s, created)

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

    def __str__(self):
        return f"(user: {self.id_user}, project: {self.id_project})"

    def update(user, projectuser):
        try:
            p = Project.objects.get(intra_id=projectuser['project']['id'])
        except:
            logging.error(f"Could not find Project with (intra_id: {projectuser['project']['id']})")
            return None
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

        log_update(pu, created)

        return pu

# This is a cursus a user is enrolled in
class CursusUser(IntraBaseModel):
    id_user = models.ForeignKey('User', on_delete=models.CASCADE)
    id_cursus = models.ForeignKey('Cursus', on_delete=models.CASCADE)
    level = models.FloatField()
    begin_at = models.DateField()

    def __str__(self):
        return f"(cursus: {self.id_cursus}, user: {self.id_user})"

    def update(user, cursususer):
        try:
            c = Cursus.objects.get(intra_id=cursususer['cursus']['id'])
        except:
            logging.error(f"Could not find Cursus with (intra_id: {cursususer['cursus']['id']})")
            return None
        cu, created = CursusUser.objects.get_or_create(intra_id=cursususer['id'],
                                                    id_user=user,
                                                    id_cursus=c,
                                                    defaults={'level': cursususer['level'],
                                                                'begin_at': cursususer['begin_at'][:10]})
        cu.level = cursususer['level']
        cu.save()

        log_update(cu, created)

        return cu

# Creates a relation between a project and a cursus, it relates which projects are in a cursus
class ProjectCursus(models.Model):
    id_cursus = models.ForeignKey('Cursus', on_delete=models.CASCADE)
    id_project = models.ForeignKey('Project', on_delete=models.CASCADE)

    def __str__(self):
        return f"(cursus: {self.id_cursus}, project: {self.id_project})"

    def update(cursus, project):
        try:
            p = Project.objects.get(intra_id=project['id'])
        except:
            logging.error(f"Could not find Project with (intra_id: {project['id']})")
            return None
        cp, created = ProjectCursus.objects.get_or_create(id_project=p, id_cursus=cursus)
        cp.save()

        log_update(cp, created)

        return cp


# Creates a relation between a skill and a cursus, it relates which skills are part of a cursus
class CursusSkill(models.Model):
    id_cursus = models.ForeignKey('Cursus', on_delete=models.CASCADE)
    id_skill = models.ForeignKey('Skill', on_delete=models.CASCADE)

    cursus_users = models.ManyToManyField('CursusUser', through='CursusUserSkill', related_name='skills')

    def __str__(self):
        return f"(cursus: {self.id_cursus}, skill: {self.id_skill})"

    def update(cursus, skill):
        try:
            s = Skill.objects.get(intra_id=skill['id'])
        except:
            logging.error(f"Could not find Skill with (intra_id: {skill['id']})")
            return None
        s = Skill.objects.get(intra_id=skill['id'])
        cs, created = CursusSkill.objects.get_or_create(id_cursus=cursus, id_skill=s)
        cs.save()

        log_update(cs, created)

        return cs

# Creates a relation between a cursus skill and a cursus user
class CursusUserSkill(models.Model):
    id_cursus_skill = models.ForeignKey('CursusSkill', on_delete=models.CASCADE)
    id_cursus_user = models.ForeignKey('CursusUser', on_delete=models.CASCADE)
    level = models.FloatField()

    def __str__(self):
        return f"(cursus skill: {self.id_cursus_skill}, user: {self.id_cursus_user.id_user})"

    def update(cursusUser, cuSkill):
        s = None
        try:
            s = Skill.objects.get(intra_id=cuSkill['id'])
        except:
            logging.error(f"Could not find Skill with (intra_id: {cuSkill['id']})")
            return None

        cs = None
        try:
            cs = CursusSkill.objects.get(id_cursus=cursusUser.id_cursus, id_skill=s)
        except:
            logging.error(f"Could not find CursusSkill with (id_cursus: {cursusUser.id_cursus.id}, id_skill: {s.id})")
            return None
        cus, created = CursusUserSkill.objects.get_or_create(id_cursus_user=cursusUser,
                                                             id_cursus_skill=cs,
                                                             defaults={'level': cuSkill['level']})
        cus.level = cuSkill['level']
        cus.save()

        log_update(cus, created)

        return cus
