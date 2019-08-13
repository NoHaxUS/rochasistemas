
from rest_framework import serializers
from rest_framework import status
from core.models import Location, League, LeagueModified, LocationModified, Store
from core.exceptions import NotAllowedException

class LeagueSerializerList(serializers.ListSerializer):	

	def to_representation(self, leagues):				
		store_id = self.context['request'].GET.get('store')
		
		for league in leagues:
			league_modified = LeagueModified.objects.filter(league=league.pk, store__pk=store_id).first()
			location_modified = LocationModified.objects.filter(location=league.location.pk, store__pk=store_id).first()
			if league_modified:
				league.priority = league_modified.priority
				league.available = league_modified.available			
			if location_modified:
				league.location.priority = location_modified.priority
				league.location.available = location_modified.available
		
		leagues.sort(key=lambda league: (league.location.priority, league.priority), reverse=True)

		return super().to_representation(leagues)


class AdmLeagueSerializerList(serializers.ListSerializer):	

	def to_representation(self, leagues):
		store = self.context['request'].user.my_store.pk		
		
		for league in leagues:
			league_modified = LeagueModified.objects.filter(league=league.pk, store__pk=store).first()
			
			if league_modified:
				league.priority = league_modified.priority
				league.available = league_modified.available

		return super().to_representation(leagues)


class MenuLeagueSerializer(serializers.HyperlinkedModelSerializer):	

	class Meta:
		model = League		
		list_serializer_class = LeagueSerializerList
		fields = ('id','name','available','priority')


class LeagueSerializer(serializers.HyperlinkedModelSerializer):

	location = serializers.SlugRelatedField(queryset = Location.objects.all(),slug_field='name')

	class Meta:
		model = League
		list_serializer_class = AdmLeagueSerializerList
		fields = ('id','name','location','priority','available')


class LeagueModifiedSerializer(serializers.HyperlinkedModelSerializer):

	league = serializers.SlugRelatedField(queryset = League.objects.all(), slug_field='pk')
	store = serializers.SlugRelatedField(read_only=True, slug_field='pk')

	def create(self, validated_data):
		user = self.context['request'].user		
		league = validated_data.get('league')		
		league_modifieds = LeagueModified.objects.filter(league__pk=league.pk, store=user.my_store)

		if league_modifieds.exists():
			league_modifieds.update(**validated_data)
			return league_modifieds.first()

		instance = LeagueModified(**validated_data)			
		instance.store = user.my_store		
		instance.save()		
		return instance
	
	class Meta:
		model = LeagueModified
		list_serializer_class = AdmLeagueSerializerList
		fields = ('league','priority','available','store')