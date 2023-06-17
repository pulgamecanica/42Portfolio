from datetime import date
from django.db import models
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import AbstractUser

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

	def serialize(self):
		return serialize('json', [self])[1:-1]

# Cursus model
class Cursus(IntraBaseModel):
	name = models.CharField(max_length=50)
	kind = models.CharField(max_length=50)

	skills = models.ManyToManyField('Skill', through='CursusSkill', related_name='cursus')

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

# Skill model
class Skill(IntraBaseModel):
	name = models.CharField(max_length=100)

	def __str__(self):
		return f"{self.name}:{self.intra_id}"

## Relations
# These are supposed to link the rest of the models together

# This is a project that a user has subscribed to
class ProjectUser(IntraBaseModel):
	id_user = models.ForeignKey('User', on_delete=models.CASCADE)
	id_project = models.ForeignKey('Project', on_delete=models.CASCADE)
	grade = models.IntegerField()
	finished = models.BooleanField(default=False)
	finished_at = models.DateTimeField()

# This is a cursus a user is enrolled in
class CursusUser(IntraBaseModel):
	id_user = models.ForeignKey('User', on_delete=models.CASCADE)
	id_cursus = models.ForeignKey('Cursus', on_delete=models.CASCADE)
	level = models.FloatField()
	begin_at = models.DateField()

# Creates a relation between a project and a cursus, it relates which projects are in a cursus
class ProjectCursus(models.Model):
	id_cursus = models.ForeignKey('Cursus', on_delete=models.CASCADE)
	id_project = models.ForeignKey('Project', on_delete=models.CASCADE)

# Creates a relation between a skill and a cursus, it relates which skills are part of a cursus
class CursusSkill(models.Model):
	id_cursus = models.ForeignKey('Cursus', on_delete=models.CASCADE)
	id_skill = models.ForeignKey('Skill', on_delete=models.CASCADE)

	cursus_users = models.ManyToManyField('CursusUser', through='CursusUserSkill', related_name='skills')

# Creates a relation between a cursus skill and a cursus user
class CursusUserSkill(models.Model):
	id_cursus_skill = models.ForeignKey('CursusSkill', on_delete=models.CASCADE)
	id_cursus_user = models.ForeignKey('CursusUser', on_delete=models.CASCADE)
	level = models.FloatField()
