from django.urls import path

from . import views

urlpatterns = [
    path('auth/callback_intra', views.callback_intra, name='callback_intra'),
]