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
from . import views

app_name = 'utils'

urlpatterns = [  
    path('update/', views.Update.as_view(), name='updating'),    
    path('populate/', views.PopulatingBD.as_view(), name='populating'),    
    path('pdf/<int:pk>', views.PDF.as_view(), name='pdf'),
    path('print/<int:pk>', views.printTicket.as_view(), name='print'),
    path('cotation_reduction/<str:percentual>', views.PercentualReductionCotation.as_view(), name='cotation_reduction'),
    path('test_url/', views.TestJson.as_view(), name='test_url'),
]
