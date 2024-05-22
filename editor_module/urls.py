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
    path('add_vic/<int:journal_id>/', views.add_vic),
    path("editor_profile/", views.editor_profile),
    path("editor_sidebar/", views.editor_sidebar),
    path("editor_register/", views.editor_register),
    path("editor_resetpassword/", views.editor_resetpassword),
    path("notifications/", views.notifications),
    path("editor_assignedjournal/", views.editor_assignedjournal),
    path("view_articles/", views.view_articles),
    path("journaldetails/", views.journaldetails),
    path("journal_details/", views.journal_details),
    path("upddetails/", views.upddetails),
    path("edit/", views.edit),
    path("e_visits/", views.e_visits),
    path("e_downloads/", views.e_downloads),
    path("remove/", views.remove),
    path('editor_contact/', views.editor_contact),
    path('notify/', views.notify),
    path('add_contact/', views.add_contact),
    path('add_editorial_board_member/', views.add_editorial_board_member),
    path('view_article/<int:article_id>/', views.view_article),
    path('approve_article/<int:article_id>/', views.approve_article),
    path('reject_article/<int:article_id>/', views.reject_article),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
