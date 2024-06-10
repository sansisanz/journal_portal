from django.contrib import admin
from django.urls import path,include
from admin_module import views

urlpatterns = [

    ################################   LOGIN PAGE  ############################################
    path("login/", views.login),
    path("index/", views.index),
    path("ea_login/", views.ea_login),
    path("logout/", views.logout),

    ################################   FORGOT PASSWORD  ############################################
    path("forgotpassword/", views.forgotpassword),
    path("updatePassword/", views.updatePassword),
    path("PasswordUpdate/", views.PasswordUpdate),
    ################################   ADD EDITOR  #########################################
    path("add_editor/", views.add_editor),
    path('addeditor/', views.addeditor, name='addeditor'),
    path("setpassword/", views.setpassword),
    path('get_editors_by_department/<int:dept_id>/', views.get_editors_by_department),
    path('remove_editor/', views.remove_editor),

    ##########################   CREATE JOURNAL ############################################
    path("create_j/", views.create_j),
    path("create_journal/", views.create_journal),

    ############################## VIEW JOURNALS  ##########################################
    path("view_j/", views.view_j),
    path("edit_j/<int:journal_id>/", views.edit_j),
    path("update_journal/<int:journal_id>/", views.update_journal),
    path("remove_journal/<int:journal_id>/", views.remove_journal),
    path('confirm_delete_journal/<int:journal_id>/', views.confirm_delete_journal),

    #################################### COUNTS   ##########################################
    path("visit_c/", views.visit_c),
    path('get_journals_by_department/', views.get_journals_by_department),
    path('get_journals_by_dept/', views.get_journals_by_dept),
    path('get_volumes_by_journal/', views.get_volumes_by_journal),
    path('get_issues_by_volume/', views.get_issues_by_volume),
    path('get_articles_by_issue/', views.get_articles_by_issue),

    ##################################   PROFILE   ##########################################
    path("adminprofile/", views.adminprofile),
    path("update_profile/", views.update_profile),

    ############################    RESET PASSWORD     #######################################
    path("adminresetpassword/", views.adminresetpassword),
    path("reset_password/", views.reset_password),

]    

