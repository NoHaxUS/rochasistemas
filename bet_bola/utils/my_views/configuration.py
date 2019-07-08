from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from user.permissions import IsAdmin
from utils.serializers.configuration import GeneralConfigurationsSerializer
from utils.models import GeneralConfigurations
from filters.mixins import FiltersMixin
import json

class GeneralConfigurationsView(FiltersMixin, ModelViewSet):
    queryset = GeneralConfigurations.objects.all()
    serializer_class = GeneralConfigurationsSerializer
    permission_classes = [IsAdmin,]

    filter_mappings = {
		'store':'store__pk',		
  	}    