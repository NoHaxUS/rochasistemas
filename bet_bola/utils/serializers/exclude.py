

class ExcludedGameSerializer(serializers.HyperlinkedModelSerializer):
	
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')
	game = serializers.SlugRelatedField(queryset = Game.objects.all(),slug_field='name')

	class Meta:
		model = ExcludedGame
		fields = ('store','game')



class ExcludedLeagueSerializer(serializers.HyperlinkedModelSerializer):
	
	store = serializers.SlugRelatedField(queryset = Store.objects.all(), slug_field='id')
	league = serializers.SlugRelatedField(queryset = League.objects.all(), slug_field='name')

	class Meta:
		model = ExcludedLeague	
		fields = ('store','league')


