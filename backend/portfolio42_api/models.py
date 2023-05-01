from datetime import date
from django.db import models
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
	intra_username = models.CharField(max_length=30, unique=True)
	intra_id = models.IntegerField(unique=True, db_index=True)
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	email = models.EmailField(max_length=130)
	intra_url = models.CharField(max_length=200);
	image_url = models.CharField();
	bio = models.TextField(max_length=800)
	updated_at = models.DateTimeField(auto_created=True, auto_now=True)
	is_admin = models.BooleanField(default=False)

	REQUIRED_FIELDS = ["email", "intra_id", "first_name", "last_name", 'intra_url']
	USERNAME_FIELD = "intra_username"

	def __str__(self):
		return "@" + self.intra_username

	def wasUpdatedToday(self):
		return self.updated_at > date.yesterday()

	def serialize(self):
		return serialize('json', [self])[1:-1]