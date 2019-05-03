from rest_framework import serializers
from core.models import GeneralConfigurations, Store

class StoreSerializer(serializers.HyperlinkedModelSerializer):	
	config = serializers.SlugRelatedField(queryset = GeneralConfigurations.objects.all(), slug_field='id')

	class Meta:
		model = Store
		fields = ('pk','fantasy','creation_date','config')