from django.contrib import admin
from django.urls import path,include
from admin_module import views

urlpatterns = [
    path("login/", views.login),
    path("index/", views.index),
    path("editor/", views.editor),
    path("journal/", views.journal),
    path("forgotpassword/", views.forgotpassword),
    path("visits/", views.visits),
    path("downloads/", views.downloads),
    path("userlist/", views.userlist),
    path("admin_profile/", views.admin_profile),
    path("admin_resetpassword/", views.admin_resetpassword),
    path("set_password/", views.set_password),
]

