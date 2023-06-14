from rest_framework import serializers
from portfolio42_api.models import User, Skill, Cursus, Project, CursusUser, CursusUserSkill

class CursusUserSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='id_cursus_skill.id_skill.name')
    skill_id = serializers.IntegerField(source='id_cursus_skill.id_skill.id')
    skill_intra_id = serializers.IntegerField(source='id_cursus_skill.id_skill.intra_id')
    class Meta():
        model = CursusUserSkill
        fields = ['id', 'skill_id', 'skill_intra_id', 'skill_name', 'level']

class CursusSerializer(serializers.ModelSerializer):
    class Meta():
        model = Cursus
        fields = ['id', 'name', 'kind']

class CursusUserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='id_cursus.id')
    intra_id = serializers.IntegerField(source='id_cursus.intra_id')
    name = serializers.CharField(source='id_cursus.name')
    kind = serializers.CharField(source='id_cursus.kind')
    skills = CursusUserSkillSerializer(many=True, read_only=True, source='cursususerskill_set')
    class Meta():
        model=CursusUser
        fields = ['id', 'intra_id', 'name', 'level', 'kind', 'skills', 'begin_at']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta():
        model = Project
        fields = ['name', 'description', 'exam', 'solo', 'intra_id']

class UserSerializer(serializers.ModelSerializer):
    # cursus = CursusSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    cursus = CursusUserSerializer(many=True, read_only=True, source='cursususer_set')
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