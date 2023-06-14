from rest_framework import serializers
from portfolio42_api.models import Cursus, Skill, CursusUser, Project

class SkillSerializer(serializers.ModelSerializer):
    class Meta():
        model = Skill
        fields = ['id', 'intra_id', 'name']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta():
        model = Project
        fields = ['id',
                  'intra_id',
                  'name',
                  'description',
                  'exam',
                  'solo']
        
class CursusUserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='id_user.id')
    intra_id = serializers.IntegerField(source='id_user.intra_id')
    intra_username = serializers.CharField(source='id_user.intra_username')
    first_name = serializers.CharField(source='id_user.first_name')
    last_name = serializers.CharField(source='id_user.last_name')
    email = serializers.EmailField(source='id_user.email')
    intra_url = serializers.CharField(source='id_user.intra_url')
    image_url = serializers.CharField(source='id_user.image_url')
    is_admin = serializers.BooleanField(source='id_user.is_admin')

    class Meta():
        model = CursusUser
        fields = ['id',
                  'intra_id',
                  'intra_username',
                  'first_name',
                  'last_name',
                  'email',
                  'intra_url',
                  'image_url',
                  'is_admin',
                  'level',
                  'begin_at']

class CursusSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    users = CursusUserSerializer(many=True, read_only=True, source='cursususer_set')
    class Meta():
        model = Cursus
        fields = ['id',
                  'intra_id',
                  'name',
                  'kind',
                  'skills',
                  'projects',
                  'users']