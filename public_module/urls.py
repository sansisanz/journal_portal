from django.contrib import admin
from django.urls import path,include
from public_module import views

urlpatterns = [
    path("p_index/", views.p_index, name="authorlogin"),

    path("p_journals/", views.p_journals),

    path("p_home/<int:id>/", views.p_home),

    path("p_ethics/<int:id>", views.p_ethics),
    path("p_guidelines/<int:id>", views.p_guidelines),
    path("p_authorreg/", views.p_authorreg),
    path("p_userreg/", views.p_userreg),
    path("p_userprofile/", views.p_userprofile),
    path("public_navbar/", views.public_navbar),
    path('p_alljournals/<int:journal_id>/', views.p_alljournals),
    path("read/", views.read),
    path("verify_author/", views.verify_author),
    path('author-registration/', views.author_registration, name='author_registration'),
    path('email_verification/', views.email_verification),
    path('author_login/', views.author_login),
    path('author_logout/', views.author_logout),
    path('issue_detail/<int:issue_id>/', views.issue_detail),
    path('read_article/', views.read_article),
    path('flipbook/<int:article_id>/', views.flipbook),
    path('download_article/<int:article_id>/',views.download_article),
    path('read_article/<int:article_id>/', views.read_article),
    path('get_client_ip/', views.get_client_ip),

]