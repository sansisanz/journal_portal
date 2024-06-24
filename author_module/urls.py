from django.conf import settings
from django.contrib import admin
from django.urls import path,include
from author_module import views
from django.conf.urls.static import static

urlpatterns = [
    path("author_sidebar", views.author_sidebar),
    path("author_index/", views.author_index),
    path("author_profile/", views.author_profile),
    path("update_profile/", views.update_profile),
    #path("author_resetpassword/", views.author_resetpassword),
    #path("author_forgotpassword/", views.author_forgotpassword),
    path("author_submitarticle/", views.author_submitarticle),
    path('article_submission/', views.article_submission, name='article_submission'),
    path('ajax_load_journals/', views.load_journals, name='ajax_load_journals'),
    path('author_review/', views.author_review),
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

