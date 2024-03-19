"""
URL configuration for journal_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from admin_module import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login,name='login'),
    path('index/', views.index,name='index'),
    path('editor/', views.editor,name='editor'),
    path('journal/', views.journal, name='journal'),
    path('forgotpassword/', views.forgotpassword, name='forgotpassword'),
    path('vd/', views.vd, name='vd'),
    path('visits/', views.visits, name='visits'),
    path('downloads/', views.downloads, name='downloads'),
    path('userlist/', views.userlist, name='userlist'),
]
