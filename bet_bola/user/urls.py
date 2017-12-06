"""bet_bola URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^home/$', views.PunterHome.as_view(), name='home'),
    url(r'^change_pass/$', views.PunterChangePass.as_view(), name='punter_change_pass'),
    url(r'^login/$', views.Login.as_view(), name='punter_login'),
    url(r'^logout/$',views.Logout.as_view(), name='punter_logout'),
    url(r'^$', views.PunterCreate.as_view(), name='create_punter'),
]
