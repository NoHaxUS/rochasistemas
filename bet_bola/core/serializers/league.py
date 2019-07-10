
from rest_framework import serializers
from core.models import Location, League, LeagueModified
from core.exceptions import NotAllowedException


class LeagueSerializerList(serializers.ListSerializer):

	def to_representation(self, leagues):
		store_id = self.context['request'].GET.get('store')
		if not store_id:
			raise NotAllowedException(detail='Banca Obrigatória')

		for league in leagues:
			league_modified = LeagueModified.objects.filter(league=league.pk, store=store_id).first()
			
			if league_modified:
				league.priority = league_modified.priority
				league.available = league_modified.available

			return super().to_representation(leagues)


class LeagueSerializer(serializers.HyperlinkedModelSerializer):

	location = serializers.SlugRelatedField(queryset = Location.objects.all(),slug_field='name')

	class Meta:
		model = League
		list_serializer_class = LeagueSerializerList
		fields = ('id','name','location','priority','available')