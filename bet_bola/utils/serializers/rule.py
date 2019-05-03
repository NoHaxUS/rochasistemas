
class RulesMessageSerializer(serializers.HyperlinkedModelSerializer):

	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model =  RulesMessage
		fields = ('text','store')

