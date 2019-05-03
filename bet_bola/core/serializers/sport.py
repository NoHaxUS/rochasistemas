
class SportSerializer(serializers.HyperlinkedModelSerializer):	

	class Meta:
		model = Sport
		fields = ('name',)