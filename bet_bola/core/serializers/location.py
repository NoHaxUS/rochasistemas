
from rest_framework import serializers
from core.models import Location

class LocationSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = Location
		fields = ('id','name','priority','visible')
