
class LocationSerializer(serializers.HyperlinkedModelSerializer):

	class Meta:
		model = Location
		fields = ('id','name','priority','visible')
