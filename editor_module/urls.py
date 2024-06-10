from django.contrib import admin
from django.urls import path,include
from editor_module import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("editor_article/", views.editor_article),
    path("editor_forgotpassword/", views.editor_forgotpassword),
    #==================Index=================================
    path("editor_index/", views.editor_index),
    path("editorprofile/", views.editorprofile),
    path("editor_sidebar/", views.editor_sidebar),
    path("editorresetpassword/", views.editorresetpassword),

    #==================ASSIGNED JOURNAL=================================
    path("assigned_journal/", views.assigned_journal),
    path('add_vic/<int:journal_id>/', views.add_vic),

    #==================ADD DETAILS=================================
    path("add_details/", views.add_details),
    path("journal_details/", views.journal_details),    

    #================== ADD EDITORIAL BOARD =================================
    path("editorialboard/", views.editorialboard),
    path('add_editorial_board_member/', views.add_editorial_board_member),

    #================== ADD NOTIFICATION =================================
    path("notifications/", views.notifications),
    path('notify/', views.notify),

    #================== ADD CONTACT =================================
    path('add_contact/', views.add_contact),
    path('editor_contact/', views.editor_contact),

    #================== JOURNAL LIST   =================================

    path("upddetails/", views.upddetails),
    path('edit_journals/<int:journal_id>/', views.edit_journals),
    path('manage_volume/<int:journal_id>/', views.manage_volume),

                         # manage volume #
    path('manage_volume/<int:journal_id>/', views.manage_volume),
    path('update_volume_name/', views.update_volume_name),
    path('remove_volume/', views.remove_volume),

                        #Manage Issues#
    path('manage_issues/<int:journal_id>/', views.manage_issues),
    path('remove_issue/', views.remove_issue),

                        #Manage Notification#
    path('manage_notification/<int:journal_id>/', views.manage_notification),
    path('edit_notification/', views.edit_notification),
    path('remove_notification/', views.remove_notification),

    #================== =================================

    #================== =================================


    path("view_articles/", views.view_articles),
    

    path("e_visits/", views.e_visits),
    
    
    path('view_article/<int:article_id>/', views.view_article),
    path('approve_article/<int:article_id>/', views.approve_article),
    path('reject_article/<int:article_id>/', views.reject_article),
    path('accept_article/<int:article_id>/', views.accept_article),
    path('contact_edit/<int:journal_id>/', views.contact_edit),
    path('details_edit/<int:journal_id>/', views.details_edit),
    path('get_notification_details/<int:notification_id>/', views.get_notification_details, name='get_notification_details'),
    path('get_editor_details/<int:editor_id>/', views.get_editor_details, name='get_editor_details'),
    path('edit_journals/<int:journal_id>/', views.edit_journals),

    #=================visit &download
    path('editor_review/', views.editor_review),
    path('get_volumes_by_journal/', views.get_volumes_by_journal),
    path('get_issues_by_volume/', views.get_issues_by_volume),
    path('get_articles_by_issue/', views.get_articles_by_issue),
    path('get_journal_visit_count/', views.get_journal_visit_count),
    path('get_article_visit_count/', views.get_articles_by_issue),
    path('get_article_download_count/', views.get_articles_by_issue),
    
    
    path('manage_aim/<int:journal_id>/', views.manage_aim),
    path('manage_gl/<int:journal_id>/', views.manage_gl),
    path('update_row/',views.update_row),
    path('remove_row/', views.remove_row),
    path('manage_ethics/<int:journal_id>/', views.manage_ethics),
    path('manage_eb/<int:journal_id>/', views.manage_eb),
    path('update_eb_member/', views.update_eb_member),
    path('remove_eb_member/', views.remove_eb_member),
    path('manage_contact/<int:journal_id>/', views.manage_contact),
    path('update_contact/', views.update_contact),
    path('remove_contact/', views.remove_contact),
    path("editor_submitarticle/", views.editor_submitarticle),
    path('earticle_submission/', views.earticle_submission, name='earticle_submission'),
    path('manage_article/<int:journal_id>/', views.manage_article),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

