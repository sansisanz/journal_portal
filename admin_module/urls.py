from django.contrib import admin
from django.urls import path,include
from admin_module import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    ################################   LOGIN PAGE  ############################################
    path("login/", views.login),
    path("index/", views.index),
    path("ea_login/", views.ea_login),
    path("logout/", views.logout),

    ################################   FORGOT PASSWORD  ############################################
    path("forgotpassword/", views.forgotpassword),
    path('reset_password/<str:token>/', views.reset_password),

    ################################   ADD EDITOR  #########################################
    path("add_editor/", views.add_editor),
    path('addeditor/', views.addeditor, name='addeditor'),
    path("set_password/", views.set_password),
    path('setpassword/', views.setpassword),
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

    ########################  MANAGE JOURNALS ##################
    path('edit_journals/<int:journal_id>/', views.edit_journals),

    #MANAGE VOLUME
    path('manage_volume/<int:journal_id>/', views.manage_volume),
    path('update_volume_name/', views.update_volume_name),
    path('remove_volume/', views.remove_volume),

    #MANAGE ISSUES
    path('manage_issue/<int:journal_id>/', views.manage_issue),
    path('remove_issue/<int:journal_id>/', views.remove_issue),
    #path('get_issues/<int:volume_id>/', views.get_issues),

    #MANAGE  NOTIFIFCATIONS
    path('manage_notification/<int:journal_id>/', views.manage_notification),
    path('edit_notification/', views.edit_notification),
    path('remove_notification/', views.remove_notification),

    #MANAGE AIM
    path('manage_aim/<int:journal_id>/', views.manage_aim),

    #MANAGE GUIDELINES
    path('manage_gl/<int:journal_id>/', views.manage_gl),
    path('update_row/',views.update_row),
    path('remove_row/', views.remove_row),

    #MANAGE ETHICS
    path('manage_ethics/<int:journal_id>/', views.manage_ethics),

    #MANAGE EDITORIAL BOARD
    path('manage_eb/<int:journal_id>/', views.manage_eb),
    path('update_eb_member/', views.update_eb_member),
    path('remove_eb_member/', views.remove_eb_member),

    #MANAGE  CONTACT
    path('manage_contact/<int:journal_id>/', views.manage_contact),
    path('update_contact/', views.update_contact),
    path('remove_contact/', views.remove_contact),

    #MANAGE ARTICLES
    path('manage_article/<int:journal_id>/', views.manage_article),
    path('edit_article/<int:article_id>/', views.edit_article),
    path('remove_article/<int:article_id>/', views.remove_article),


]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  

