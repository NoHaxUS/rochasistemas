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
from django.urls import path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from rest_framework.authtoken import views
import rest_framework

def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [ 
    path('api-auth/', include('rest_framework.urls')),        
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('', include('ticket.urls', namespace='ticket')),
    path('', include('utils.urls', namespace='utils')),
    path('', include('user.urls', namespace='user')),
    path('', include('history.urls', namespace='history')),
    path('', include('cashier.urls', namespace='cashier')),
    path('sentry-debug/', trigger_error),
]
