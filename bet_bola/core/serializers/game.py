from rest_framework import serializers
from core.serializers.cotation import StandardCotationSerializer
from core.models import League, Game, Location


class GameSerializerForHome(serializers.HyperlinkedModelSerializer):
	standard_cotations = StandardCotationSerializer(many=True)

	class Meta:
		model = Game				
		fields = ('id','name','start_date','standard_cotations')

	def get_location(self, game):
		return game.league.location.name

	
class GameSerializer(serializers.HyperlinkedModelSerializer):			

	standard_cotations = StandardCotationSerializer(many=True)	
	league = serializers.SlugRelatedField(queryset=League.objects.all(), slug_field='name')
	location = serializers.SerializerMethodField()

	class Meta:
		model = Game				
		fields = ('id','name','start_date','status','league','location','standard_cotations')

	def get_location(self, game):
		return game.league.location.name



class GameListSerializer(serializers.HyperlinkedModelSerializer):			

	league = serializers.SlugRelatedField(slug_field='name', read_only=True)
	location = serializers.SerializerMethodField()

	class Meta:
		model = Game				
		fields = ('id','name','start_date','league','location', 'available')	

	def get_location(self, game):
		return game.league.location.name


class GameTableSerializer(serializers.HyperlinkedModelSerializer):			

	cotations = serializers.SerializerMethodField()
	league = serializers.SlugRelatedField(queryset=League.objects.all(), slug_field='name')
	location = serializers.SerializerMethodField()

	class Meta:
		model = Game				
		fields = ('id','name','start_date','status','league','location','cotations')

	def get_location(self, game):
		return game.league.location.name
	
	def get_cotations(self, game):
		cotations = game.my_cotations
		serializer = StandardCotationSerializer(cotations,many=True,context={'context':self.context})
		return serializer.data


class TodayGamesSerializer(serializers.HyperlinkedModelSerializer):
	league = serializers.CharField(source='name')
	location = serializers.SlugRelatedField(queryset=Location.objects.all(), slug_field='name')
	games = serializers.SerializerMethodField()

	class Meta:
		model = League
		fields = ('id','league','location','games')

	def get_games(self, league):			
		qs = league.games

		serializer = GameSerializerForHome(qs ,many=True, context={'context':self.context})
		return serializer.data


class CountryGameTodaySerializers(serializers.HyperlinkedModelSerializer):
	itens = TodayGamesSerializer(many=True, source='my_leagues')

	class Meta:
		model = Location
		fields = ('id','name','itens')	