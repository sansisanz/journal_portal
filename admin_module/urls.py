from django.contrib import admin
from django.urls import path,include
from admin_module import views

urlpatterns = [
    path("login/", views.login),
    path("index/", views.index),
    path("forgotpassword/", views.forgotpassword),
    path("visit_c/", views.visit_c),
    path("download_c/", views.download_c),
    path("userlist/", views.userlist),
    path("adminprofile/", views.adminprofile),
    path("adminresetpassword/", views.adminresetpassword),
    path("set_password/", views.set_password),
    path("create_j/", views.create_j),
    path("view_j/", views.view_j),
    path("edit_j/", views.edit_j),
    path("add_editor/", views.add_editor),
    path("ea_login/", views.ea_login),
    path("logout/", views.logout),
    path('addeditor/', views.addeditor, name='addeditor'),
    path("setpassword/", views.setpassword),
]

