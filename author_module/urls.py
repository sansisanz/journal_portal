from django.contrib import admin
from django.urls import path,include
from author_module import views

urlpatterns = [
    path("author_index/", views.author_index),
    path("author_profile/", views.author_profile),
    path("author_resetpassword/", views.author_resetpassword),
    path("author_forgotpassword/", views.author_forgotpassword),
    path("author_submitarticle/", views.author_submitarticle),
]