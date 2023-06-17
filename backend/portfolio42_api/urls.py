from django.urls import path, include
from portfolio42_api.models import Cursus, Project, Skill, User 
from rest_framework import routers, viewsets
from portfolio42_api import views
# from serializers import ProjectSerializer, UserSerializer, SkillSerializer, CursusSerializer
from portfolio42_api.serializers import *

# ViewSets define the view behavior.
class CursusViewSet(viewsets.ModelViewSet):
    queryset = Cursus.objects.all()
    serializer_class = CursusSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'cursus', CursusViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'skills', SkillViewSet)
router.register(r'users', UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    path('auth/login', views.login_intra, name='login_intra'),
    path('auth/callback_intra', views.callback_intra, name='callback_intra'),
]