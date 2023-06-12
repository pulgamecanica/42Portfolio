from rest_framework import serializers
from portfolio42_api.models import User, Skill, Cursus, Project
class SkillSerializer(serializers.ModelSerializer):
    class Meta():
        model = Skill
        fields = ['name', 'intra_id']

class CursusSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    class Meta():
        model = Cursus
        fields = ['name', 'kind', 'intra_id', 'skills']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta():
        model = Project
        fields = ['name', 'description', 'exam', 'solo', 'intra_id']

class UserSerializer(serializers.ModelSerializer):
    cursus = CursusSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    class Meta():
        model = User
        fields = ['id',
                  'intra_id',
                  'intra_username',
                  'first_name',
                  'last_name',
                  'email',
                  'intra_url',
                  'image_url',
                  'cursus',
                  'projects',
                  'is_admin',]