"""
URL configuration for senior_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from app import views


urlpatterns = [
    path('', views.Customer.index),
    path('cum/login/', views.Customer.login),


    path('clt/', views.Client.index),
    path("clt/basic/", views.Client.basic),
    path("clt/menu/", views.Client.menu),
    path('clt/signup/', views.Client.signup),
    path('clt/login/', views.Client.login),
]
