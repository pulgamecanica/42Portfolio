from rest_framework import serializers
from portfolio42_api.models import Cursus

class CursusSerializer(serializers.ModelSerializer):
    class Meta():
        model = Cursus
        fields = ['name', 'kind', 'intra_id']