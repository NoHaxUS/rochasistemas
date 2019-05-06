from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from user.models import Admin
from user.permissions import IsSuperUser, StoreGiven
from user.serializers.admin import AdminSerializer

class AdminView(ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer    

    def get_permissions(self):
        if self.action == 'create':            
            permission_classes = [IsSuperUser, StoreGiven]
        else:
            permission_classes = [IsSuperUser,]
        return [permission() for permission in permission_classes]