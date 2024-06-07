from django.contrib import admin
from django.urls import path,include
from editor_module import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("editor_article/", views.editor_article),
    path("editorialboard/", views.editorialboard),
    path("editor_forgotpassword/", views.editor_forgotpassword),
    path("editor_index/", views.editor_index),
    path("editorprofile/", views.editorprofile),
    path("editor_sidebar/", views.editor_sidebar),
    path("editorresetpassword/", views.editorresetpassword),
    path("notifications/", views.notifications),
    path("editor_assignedjournal/", views.editor_assignedjournal),
    path("view_articles/", views.view_articles),
    path("journaldetails/", views.journaldetails),
    path("journal_details/", views.journal_details),
    path("upddetails/", views.upddetails),
    path("e_visits/", views.e_visits),
    path('editor_contact/', views.editor_contact),
    path('notify/', views.notify),
    path('add_contact/', views.add_contact),
    path('add_editorial_board_member/', views.add_editorial_board_member),
    path('view_article/<int:article_id>/', views.view_article),
    path('approve_article/<int:article_id>/', views.approve_article),
    path('reject_article/<int:article_id>/', views.reject_article),
    path('accept_article/<int:article_id>/', views.accept_article),
    path('contact_edit/<int:journal_id>/', views.contact_edit),
    path('details_edit/<int:journal_id>/', views.details_edit),
    path('get_notification_details/<int:notification_id>/', views.get_notification_details, name='get_notification_details'),
    path('get_editor_details/<int:editor_id>/', views.get_editor_details, name='get_editor_details'),
    path('edit_journals/<int:journal_id>/', views.edit_journals),
    path('editor_review/', views.editor_review),
    path('get_journals_by_editor/', views.get_journals_by_editor),
    path('get_volumes_by_journal/', views.get_volumes_by_journal),
    path('get_issues_by_volume/', views.get_issues_by_volume),
    path('get_articles_by_issue/', views.get_articles_by_issue),
    path('get_journal_visit_count/', views.get_journal_visit_count),
    path('get_article_visit_count/', views.get_articles_by_issue),
    path('get_article_download_count/', views.get_articles_by_issue),
    path('update_volume_name/', views.update_volume_name),
    path('remove_volume/', views.remove_volume),
    #path('get_issues/', views.get_issues),
    #path('update_issue/', views.update_issue),
    #path('remove_issue/', views.remove_issue),
    path('manage_volume/<int:journal_id>/', views.manage_volume),
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

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

