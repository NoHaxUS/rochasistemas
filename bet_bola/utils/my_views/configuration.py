from rest_framework.viewsets import ModelViewSet
from utils.serializers.configuration import GeneralConfigurationsSerializer
from utils.models import GeneralConfigurations
from filters.mixins import FiltersMixin

class GeneralConfigurationsView(FiltersMixin, ModelViewSet):
    queryset = GeneralConfigurations.objects.all()
    serializer_class = GeneralConfigurationsSerializer

    filter_mappings = {
		'store':'store__pk',		
	}