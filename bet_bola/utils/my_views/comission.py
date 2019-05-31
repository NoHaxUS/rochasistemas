from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from utils.serializers.comission import ComissionSerializer
from core.permissions import StoreIsRequired, UserIsFromThisStore
from utils.models import Comission
from filters.mixins import FiltersMixin

class ComissionView(FiltersMixin, ModelViewSet):
	queryset = Comission.objects.all()
	serializer_class = ComissionSerializer
	
	filter_mappings = {
		'seller': 'seller_related',
		'store':'store'
	}
