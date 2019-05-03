
from rest_framework import serializers
from core.models import Location, League


class LeagueSerializer(serializers.HyperlinkedModelSerializer):

	location = serializers.SlugRelatedField(queryset = Location.objects.all(),slug_field='name')

	class Meta:
		model = League
		fields = ('id','name','location','priority','visible')