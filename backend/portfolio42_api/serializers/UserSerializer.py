from rest_framework import serializers
from portfolio42_api.models import User
from portfolio42_api.serializers import ProjectSerializer, CursusSerializer

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