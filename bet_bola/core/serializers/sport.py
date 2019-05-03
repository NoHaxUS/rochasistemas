from rest_framework import serializers
from core.models import Sport

class SportSerializer(serializers.HyperlinkedModelSerializer):	

	class Meta:
		model = Sport
		fields = ('name',)