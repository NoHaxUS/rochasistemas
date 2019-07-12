
from rest_framework import serializers
from rest_framework import status
from core.models import Location, League, LeagueModified, Store
from core.exceptions import NotAllowedException

class LeagueSerializerList(serializers.ListSerializer):

	def to_representation(self, leagues):
		store = self.context['request'].user.my_store		

		for league in leagues:
			league_modified = LeagueModified.objects.filter(league=league.pk, store=store).first()						
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
		list_serializer_class = LeagueSerializerList
		fields = ('league','priority','available','store')