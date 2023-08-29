from django.contrib import admin
from .models import User, Project, Skill, Cursus

# Register your models here.
admin.site.register(User)
admin.site.register(Project)
admin.site.register(Skill)
admin.site.register(Cursus)