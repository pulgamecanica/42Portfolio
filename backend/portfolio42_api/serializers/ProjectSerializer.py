from rest_framework import serializers
from portfolio42_api.models import Project

class ProjectSerializer(serializers.ModelSerializer):
    class Meta():
        model = Project
        fields = ['name', 'description', 'exam', 'solo', 'intra_id']