from rest_framework import serializers
from portfolio42_api.models import User, Skill, Cursus, Project, CursusUser, CursusUserSkill

class SkillSerializer(serializers.ModelSerializer):
    class Meta():
        model = Skill
        fields = ['id', 'name', 'intra_id']

class CursusUserSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True, source='id_cursus_skill.id_skill')
    class Meta():
        model = CursusUserSkill
        fields = ['id', 'level', 'skill']

class CursusSerializer(serializers.ModelSerializer):
    class Meta():
        model = Cursus
        fields = ['id', 'name', 'kind']

class CursusUserSerializer(serializers.ModelSerializer):
    cursus = CursusSerializer(read_only=True, source='id_cursus')
    skills = CursusUserSkillSerializer(many=True, read_only=True, source='cursususerskill_set')
    class Meta():
        model=CursusUser
        fields = ['cursus', 'level', 'begin_at', 'skills']

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