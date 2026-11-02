from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cv/', views.download_cv, name='download_cv'),
    path('github-stats/', views.github_stats, name='github_stats'),
]
