from rest_framework import serializers
from core.models import GeneralConfigurations, Store

class StoreSerializer(serializers.ModelSerializer):
	class Meta:
		model = Store
		fields = ('pk','fantasy','creation_date')