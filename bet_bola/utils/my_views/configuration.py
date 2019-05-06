from rest_framework.viewsets import ModelViewSet
from utils.serializers.configuration import GeneralConfigurationsSerializer
from utils.models import GeneralConfigurations

class GeneralConfigurationsView(ModelViewSet):
    queryset = GeneralConfigurations.objects.all()
    serializer_class = GeneralConfigurationsSerializer    

