from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from user.views.punter import PunterView
from user.views.seller import SellerView
from user.views.manager import ManagerView
from user.views.admin import AdminView

app_name = 'user'

router = DefaultRouter()
router.register(r'managers', ManagerView)
router.register(r'sellers', SellerView)
router.register(r'punters', PunterView)
router.register(r'admins', AdminView)


urlpatterns = router.urls