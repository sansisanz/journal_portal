from django.contrib import admin
from django.urls import path,include
from admin_module import views

urlpatterns = [
    path("login/", views.login),
    path("index/", views.index),
    path("forgotpassword/", views.forgotpassword),
    path("visit_c/", views.visit_c),
    path("userlist/", views.userlist),
    path("adminprofile/", views.adminprofile),
    path("adminresetpassword/", views.adminresetpassword),
    path("set_password/", views.set_password),
    path("create_j/", views.create_j),
    path("view_j/", views.view_j),
    path("edit_j/<int:journal_id>/", views.edit_j),
    path("add_editor/", views.add_editor),
    path("ea_login/", views.ea_login),
    path("logout/", views.logout),
    path('addeditor/', views.addeditor, name='addeditor'),
    path("setpassword/", views.setpassword),
    path("create_journal/", views.create_journal),
    path("update_profile/", views.update_profile),
    path("view_profile/", views.view_profile),
    path("reset_password/", views.reset_password),
    path("update_journal/<int:journal_id>/", views.update_journal),
    path("remove_journal/<int:journal_id>/", views.remove_journal),
    path('confirm_delete_journal/<int:journal_id>/', views.confirm_delete_journal),
    path('remove_editor/', views.remove_editor),
    path('get_journals_by_dept/', views.get_journals_by_dept),
    path('get_journals_by_department/', views.get_journals_by_department),
    path('get_volumes_by_journal/', views.get_volumes_by_journal),
    path('get_issues_by_volume/', views.get_issues_by_volume),
    path('get_articles_by_issue/', views.get_articles_by_issue),

]    

