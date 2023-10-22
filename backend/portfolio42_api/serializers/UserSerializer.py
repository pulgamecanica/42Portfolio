from rest_framework import serializers
from portfolio42_api.models import User, ProjectUser, CursusUser, CursusUserSkill

class CursusUserSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='id_cursus_skill.id_skill.name')
    skill_id = serializers.IntegerField(source='id_cursus_skill.id_skill.id')
    skill_intra_id = serializers.IntegerField(source='id_cursus_skill.id_skill.intra_id')
    class Meta():
        model = CursusUserSkill
        fields = ['id',
                  'skill_id',
                  'skill_intra_id',
                  'skill_name',
                  'level']

class CursusUserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='id_cursus.id')
    intra_id = serializers.IntegerField(source='id_cursus.intra_id')
    name = serializers.CharField(source='id_cursus.name')
    kind = serializers.CharField(source='id_cursus.kind')
    skills = CursusUserSkillSerializer(many=True, read_only=True, source='cursususerskill_set')
    class Meta():
        model = CursusUser
        fields = ['id',
                  'intra_id',
                  'name',
                  'level',
                  'kind',
                  'skills',
                  'begin_at']

class ProjectUserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='id_project.name')
    description = serializers.CharField(source='id_project.description')
    exam = serializers.BooleanField(source='id_project.exam')
    solo = serializers.BooleanField(source='id_project.solo')
    class Meta():
        model = ProjectUser
        fields = ['id',
                  'name',
                  'description',
                  'exam',
                  'solo',
                  'grade',
                  'finished',
                  'finished_at']

class UserSerializer(serializers.ModelSerializer):
    projects = ProjectUserSerializer(many=True, read_only=True, source='projectuser_set')
    cursus = CursusUserSerializer(many=True, read_only=True, source='cursususer_set')
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
                  'cursus',
                  'projects',
                  'is_admin']