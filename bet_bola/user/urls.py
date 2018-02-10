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
from . import views

app_name = 'user'

urlpatterns = [
    path('punter/home/', views.PunterHome.as_view(), name='user_punter_home'),
    path('punter/register/', views.PunterRegister.as_view(), name='user_punter_register'),
    path('seller/home/', views.SellerHome.as_view(), name='user_seller_home'),
    path('seller/payed_bets/', views.SellerPayedBets.as_view(), name='user_seller_payed_bets'),
    path('seller/validate_ticket/', views.SellerValidateTicket.as_view(), name='user_seller_validate_ticket'),
    path('seller/punter_payment/', views.SellerPayPunter.as_view(), name='user_seller_punter_payment'),
    path('change_password/',views.UserPasswordChange.as_view(), name='user_change_password'),
    path('login/', views.UserLogin.as_view(), name='user_login'),
    path('logout/',views.UserLogout.as_view(), name='user_logout'),
]