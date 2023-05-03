from django.urls import path

from . import views

urlpatterns = [
    path('', views.api_home, name='api_home'),
    path('auth/login', views.login_intra, name='login_intra'),
    path('auth/callback_intra', views.callback_intra, name='callback_intra'),
]