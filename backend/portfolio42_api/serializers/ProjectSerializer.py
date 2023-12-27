from rest_framework import serializers
from portfolio42_api.models import Project, User, Cursus, ProjectTranslation
import re

class CursusSerializer(serializers.ModelSerializer):
    class Meta():
        model = Cursus
        fields= ['id', 'intra_id', 'name', 'kind']

class UserSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ['id',
                  'intra_id',
                  'username',
                  'first_name',
                  'last_name',
                  'email',
                  'intra_url',
                  'image_url',
                  'is_admin',]

class ProjectSerializer(serializers.ModelSerializer):
    cursus = CursusSerializer(many=True, read_only=True)
    users = UserSerializer(many=True, read_only=True)
    class Meta():
        model = Project
        fields = ['name',
                  'exam',
                  'solo',
                  'intra_id',
                  'cursus',
                  'users']

    def to_representation(self, instance):
        instance_data = super().to_representation(instance)
        lang_raw = self.context['request'].GET.get('lang','default')
        langs = []
        # lang_raw validation
        if (re.fullmatch('^\[(?:[A-Z]+-[A-Z]+|default)(?:,(?:[A-Z]+-[A-Z]+|default))*\]$', lang_raw)):
            langs = lang_raw[1:-1].split(',')
        langs.append('default')
        for lang in langs:
            try:
                pt = ProjectTranslation.objects.get(id_language__name_short=lang,id_project=instance)
                print(f"found correct ${lang}")
                instance_data['description'] = pt.description
                instance_data['description_bonus'] = pt.description_bonus
                instance_data['append_bonus'] = pt.bonus_append
                break
            except ProjectTranslation.DoesNotExist:
                pass
        return instance_data