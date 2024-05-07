from django.contrib import admin
from django.urls import path,include
from editor_module import views

urlpatterns = [
    path("editor_article/", views.editor_article),
    path("editorialboard/", views.editorialboard),
    path("editor_forgotpassword/", views.editor_forgotpassword),
    path("editor_index/", views.editor_index),
    path("editor_journal/", views.editor_journal),
    path("editor_login/", views.editor_login),
    path("editor_profile/", views.editor_profile),
    path("editor_register/", views.editor_register),
    path("editor_resetpassword/", views.editor_resetpassword),
    path("editor_updates/", views.editor_updates),
    path("editor_assignedjournal/", views.editor_assignedjournal),
    path("uploadArticle/", views.uploadArticle),
    path("journaldetails/", views.journaldetails),
    path("upddetails/", views.upddetails),
    path("edit/", views.edit),
    path("e_visits/", views.e_visits),
    path("e_downloads/", views.e_downloads),
    path("remove/", views.remove),
    path('editor_contact/', views.editor_contact),
]