from django.contrib import admin
from .models import User, Project, Skill, Cursus, TranslationLanguage, ProjectTranslation

class UserAdmin(admin.ModelAdmin):
	search_fields = ['username', 'first_name', 'last_name', 'email', 'intra_id']

class ProjectAdmin(admin.ModelAdmin):
	search_fields = ['name', 'description', 'intra_id']

class SkillAdmin(admin.ModelAdmin):
	search_fields = ['name', 'intra_id']

class CursusAdmin(admin.ModelAdmin):
	search_fields = ['name', 'kind', 'intra_id']

class TranslationLanguageAdmin(admin.ModelAdmin):
	search_fields = ['name_short', 'name_full']

class ProjectTranslationAdmin(admin.ModelAdmin):
	list_filter = ['id_project__name', 'id_language__name_short']
	search_fields = ['id_project__name', 'id_language__name_short']

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(Cursus, CursusAdmin)
admin.site.register(TranslationLanguage, TranslationLanguageAdmin)
admin.site.register(ProjectTranslation, ProjectTranslationAdmin)