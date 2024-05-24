from django.contrib import admin
from django.urls import path,include
from public_module import views

urlpatterns = [
    path("p_index/", views.p_index, name="authorlogin"),
    path("p_alljournals/", views.p_alljournals),
    path("p_ethics/<int:id>", views.p_ethics),
    path("p_guidelines/<int:id>", views.p_guidelines),
    path("p_j/", views.p_j),
    path("p_journals/", views.p_journals),
    path("p_authorreg/", views.p_authorreg),
    path("p_userreg/", views.p_userreg),
    path("p_userprofile/", views.p_userprofile),
    path("public_navbar/", views.public_navbar),
    path("p_home/<int:id>", views.p_home),
    path("read/", views.read),
    path("verify_author/", views.verify_author),
    path('author-registration/', views.author_registration, name='author_registration'),
    path('email_verification/', views.email_verification),
    path('author_login/', views.author_login),
    path('author_logout/', views.author_logout),
    path('p_volume/', views.p_volume),

]