from django.contrib import admin
from django.urls import path,include
from editor_module import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    #INDEX
    path("editor_index/", views.editor_index),
    path("editorprofile/", views.editorprofile),
    path("editor_sidebar/", views.editor_sidebar),
    path("editorresetpassword/", views.editorresetpassword),

    #ASSIGNED JOURNAL
    path("assigned_journal/", views.assigned_journal),
    path('add_vic/<int:journal_id>/', views.add_vic),
    path('edit_journal/<int:journal_id>/', views.edit_journal),
    path('manage_volume/<int:journal_id>/', views.manage_volume),

    #ADD DETAILS
    path("add_details/", views.add_details),
    path("journal_details/", views.journal_details),    

    #ADD EDITORIAL BOARD
    path("editorialboard/", views.editorialboard),
    path('add_editorial_board_member/', views.add_editorial_board_member),

    #ADD NOTIFICATION
    path("notifications/", views.notifications),
    path('notify/', views.notify),

    # ADD CONTACT 
    path('add_contact/', views.add_contact),
    path('editor_contact/', views.editor_contact),

    #VIEW ARTICLES
    path("view_articles/", views.view_articles),
    path('view_article/<int:article_id>/', views.view_article),
    path('approve_article/<int:article_id>/', views.approve_article),
    path('reject_article/<int:article_id>/', views.reject_article),
    path('accept_article/<int:article_id>/', views.accept_article),

    #visit &download 
    path("e_visits/", views.e_visits),

    path('get_volumes_by_journal/', views.get_volumes_by_journal),
    path('get_issues_by_volume/', views.get_issues_by_volume),
    path('get_articles_by_issue/', views.get_articles_by_issue),
    path('get_journal_visit_count/', views.get_journal_visit_count),
    path('get_article_visit_count/', views.get_articles_by_issue),
    path('get_article_download_count/', views.get_articles_by_issue),
    

    #SUBMIT ARTICLE
    path('editor_submitarticle/', views.editor_submitarticle),
    path('earticle_submission/', views.earticle_submission),
    path('ajax_load_journals/', views.ajax_load_journals),

    #REVIEWS
    path('editor_review/', views.editor_review),
    path('view_reviews/<int:article_id>/', views.view_reviews),    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

