from rest_framework import serializers
from core.serializers.cotation import StandardCotationSerializer, CotationSerializerForTable
from core.serializers.league import LeagueSerializerList
from core.models import League, Game, Location, GameModified


class GameSerializerList(serializers.ListSerializer):

	def to_representation(self, games):
		store = self.context['request'].user.my_store		

		for game in games:
			game_modified = GameModified.objects.filter(game=game.pk, store=store).first()						
			if game_modified:
				game.available = game_modified.available

		return super().to_representation(games)


class GameSerializerForHome(serializers.HyperlinkedModelSerializer):
	standard_cotations = StandardCotationSerializer(many=True)

	class Meta:
		model = Game	
			
		fields = ('id','name','start_date','standard_cotations')

	def get_location(self, game):
		return game.league.location.name


class GameSerializerForTable(serializers.HyperlinkedModelSerializer):
	cotations = serializers.SerializerMethodField()

	def get_cotations(self, game):
		cotations = game.my_cotations
		serializer = CotationSerializerForTable(cotations, many=True)
		return serializer.data

	class Meta:
		model = Game				
		fields = ('id','name','cotations','start_date')

	
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
		list_serializer_class = GameSerializerList				
		fields = ('id','name','start_date','league','location', 'available')	

	def get_location(self, game):
		return game.league.location.name


class GameTableSerializer(serializers.HyperlinkedModelSerializer):
	league = serializers.CharField(source='name')
	location = serializers.SlugRelatedField(queryset=Location.objects.all(), slug_field='name')
	games = serializers.SerializerMethodField()

	class Meta:
		model = League
		fields = ('id','league','location','games')

	def get_games(self, league):			
		qs = league.games

		serializer = GameSerializerForTable(qs, many=True, context={'context':self.context})
		return serializer.data


class TodayGamesSerializer(serializers.HyperlinkedModelSerializer):
	league = serializers.CharField(source='name')
	location = serializers.SlugRelatedField(queryset=Location.objects.all(), slug_field='name')
	games = serializers.SerializerMethodField()

	class Meta:
		model = League
		list_serializer_class = LeagueSerializerList
		fields = ('id','league','location','games')

	def get_games(self, league):			
		qs = league.games		
		serializer = GameSerializerForHome(qs, many=True, context={'context':self.context})
		return serializer.data
		


class CountryGameTodaySerializers(serializers.HyperlinkedModelSerializer):
	itens = TodayGamesSerializer(many=True, source='my_leagues')

	class Meta:
		model = Location
		fields = ('id','name','itens')	
	
