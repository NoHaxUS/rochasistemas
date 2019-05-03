from rest_framework.viewsets import ModelViewSet
from core.models import Store
from core.serializers.store import StoreSerializer
from core.permissions import StorePermission

class StoreView(ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [StorePermission,]

