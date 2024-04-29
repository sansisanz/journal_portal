from django.contrib import admin
from django.urls import path,include
from public_module import views

urlpatterns = [
    path("p_index/", views.p_index),
    path("p_alljournals/", views.p_alljournals),
    path("p_ethics/", views.p_ethics),
    path("p_guidelines/", views.p_guidelines),
    path("p_j/", views.p_j),
    path("p_journals/", views.p_journals),
    path("p_authorreg/", views.p_authorreg),
    path("p_userreg/", views.p_userreg),
    path("p_userprofile/", views.p_userprofile)
    
]