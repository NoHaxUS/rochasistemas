from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from user.models import Admin
from core.permissions import StoreIsRequired
from user.permissions import AdminUserViewPermission
from user.serializers.admin import AdminSerializer

class AdminView( ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer
    permission_classes = [AdminUserViewPermission]
