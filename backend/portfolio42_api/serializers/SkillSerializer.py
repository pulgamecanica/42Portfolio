from rest_framework import serializers
from portfolio42_api.models import Skill

class SkillSerializer(serializers.ModelSerializer):
    class Meta():
        model = Skill
        fields = ['name', 'intra_id']