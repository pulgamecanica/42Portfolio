from rest_framework import serializers
from portfolio42_api.models import Skill, Cursus

class CursusSerializer(serializers.ModelSerializer):
    class Meta():
        model = Cursus
        fields = ['id', 'intra_id', 'name', 'kind']

class SkillSerializer(serializers.ModelSerializer):
    cursus = CursusSerializer(many=True, read_only=True)
    class Meta():
        model = Skill
        fields = ['id', 'intra_id', 'name', 'cursus']