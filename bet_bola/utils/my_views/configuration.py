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

    def perform_create(self, serializer):		
        store = self.request.user.my_store				
        data = serializer.validated_data
        
        if GeneralConfigurations.objects.filter(store=store).exists():
            configuration = GeneralConfigurations.objects.filter(store=store).update(**data)                        
            return GeneralConfigurations.objects.filter(store=store).first()
        return GeneralConfigurations.objects.create(store=store, **data)

