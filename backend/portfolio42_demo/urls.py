from django.urls import path
from portfolio42_demo import views

urlpatterns = [
    path('', views.home_page, name="home"),
    path('profile', views.profile, name='profile'),
    # path('projects-badge', views.badge, name='projects-badge'),
]