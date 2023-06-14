from rest_framework import serializers
from portfolio42_api.models import Project, User, Cursus

class CursusSerializer(serializers.ModelSerializer):
    class Meta():
        model = Cursus
        fields= ['id', 'intra_id', 'name', 'kind']

class UserSerializer(serializers.ModelSerializer):
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
                  'is_admin',]

class ProjectSerializer(serializers.ModelSerializer):
    cursus = CursusSerializer(many=True, read_only=True)
    users = UserSerializer(many=True, read_only=True)
    class Meta():
        model = Project
        fields = ['name',
                  'description',
                  'exam',
                  'solo',
                  'intra_id',
                  'cursus',
                  'users']