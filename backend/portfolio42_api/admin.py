from django.contrib import admin
from .models import User, Project, Skill, Cursus

class UserAdmin(admin.ModelAdmin):
	search_fields = ['username', 'first_name', 'last_name', 'email', 'intra_id']

class ProjectAdmin(admin.ModelAdmin):
	search_fields = ['name', 'description', 'intra_id']

class SkillAdmin(admin.ModelAdmin):
	search_fields = ['name', 'intra_id']

class CursusAdmin(admin.ModelAdmin):
	search_fields = ['name', 'kind', 'intra_id']

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(Cursus, CursusAdmin)