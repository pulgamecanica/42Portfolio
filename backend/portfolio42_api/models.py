from datetime import date
from django.db import models
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import AbstractUser

# User model
class User(AbstractUser):
	intra_username = models.CharField(max_length=30, unique=True)
	intra_id = models.IntegerField(unique=True, db_index=True)
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	email = models.EmailField(max_length=130)
	intra_url = models.CharField(max_length=200)
	image_url = models.CharField(max_length=800)
	updated_at = models.DateTimeField(auto_created=True, auto_now=True)
	is_admin = models.BooleanField(default=False)

	REQUIRED_FIELDS = ["email", "intra_id", "first_name", "last_name", 'intra_url']
	USERNAME_FIELD = "intra_username"

	def __str__(self):
		return "@" + self.intra_username

	def was_updated_today(self):
		return self.updated_at > date.yesterday()

	def serialize(self):
		return serialize('json', [self])[1:-1]

# Cursus model
class Cursus(models.Model):
	intra_id = models.IntegerField(unique=True, db_index=True)
	name = models.CharField(max_length=50)
	kind = models.CharField(max_length=50)
	updated_at = models.DateTimeField(auto_created=True, auto_now=True)

	def __str__(self):
		return f"{self.name}:{self.intra_id}"

	def was_updated_today(self):
		return self.updated_at > date.yesterday()

# Project model
class Project(models.Model):
	intra_id = models.IntegerField(unique=True, db_index=True)
	name = models.CharField(max_length=50)
	description = models.TextField(max_length=2000)
	exam = models.BooleanField(default=False)
	solo = models.BooleanField(default=True)
	updated_at = models.DateTimeField(auto_created=True, auto_now=True)
	
	def __str__(self):
		return f"{self.name}:{self.intra_id}"

	def was_updated_today(self):
		return self.updated_at > date.yesterday()

# Skill model
class Skill(models.Model):
	intra_id = models.IntegerField(unique=True, db_index=True)
	name = models.CharField(max_length=100)
	updated_at = models.DateTimeField(auto_created=True, auto_now=True)

	def __str__(self):
		return f"{self.name}:{self.intra_id}"

	def was_updated_today(self):
		return self.updated_at > date.yesterday()

## Relations
# These are supposed to link the rest of the models together

# This is a project that a user has subscribed to
class ProjectUser(models.Model):
	id_user = models.ForeignKey(User, on_delete=models.CASCADE)
	id_project = models.ForeignKey(Project, on_delete=models.CASCADE)
	grade = models.IntegerField()
	finished = models.BooleanField(default=False)
	finished_at = models.DateTimeField()
	updated_at = models.DateTimeField(auto_created=True, auto_now=True)

# Creates a relation between a project and a cursus, it relates which projects are in a cursus
class ProjectCursus(models.Model):
	id_cursus = models.ForeignKey(Cursus, on_delete=models.CASCADE)
	id_project = models.ForeignKey(Project, on_delete=models.CASCADE)

# Creates a relation between a skill and a cursus, it relates which skills are part of a cursus
class CursusSkill(models.Model):
	id_cursus = models.ForeignKey(Cursus, on_delete=models.CASCADE)
	id_skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

# Creates a relation between ProjectUser and Cursus, it relates which project users are part of which cursus
class ProjectUserCursus(models.Model):
	id_cursus = models.ForeignKey(Cursus, on_delete=models.CASCADE)
	id_project_user = models.ForeignKey(ProjectUser, on_delete=models.CASCADE)
