
from rest_framework import serializers
from core.serializers.league import MenuLeagueSerializer
from core.models import Location, LocationModified

class AdmLocationSerializerList(serializers.ListSerializer):
    
	def to_representation(self, locations):
		store = self.context['request'].user.my_store

		for location in locations:
			location_modified = LocationModified.objects.filter(location=location.pk, store=store).first()						
			if location_modified:
				location.priority = location_modified.priority
				location.available = location_modified.available 
				
		locations.sort(key=lambda location: location.priority, reverse=True)

		return super().to_representation(locations)

class LocationSerializerList(serializers.ListSerializer):

	def to_representation(self, locations):
		store = self.context['request'].GET.get('store')

		for location in locations:
			location_modified = LocationModified.objects.filter(location=location.pk, store=store).first()						
			if location_modified:
				location.priority = location_modified.priority
				location.available = location_modified.available 
				
		locations.sort(key=lambda location: location.priority, reverse=True)

		return super().to_representation(locations)


class LocationSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Location
        list_serializer_class = AdmLocationSerializerList
        fields = ('id','name','priority','available')


class MenuViewSerializer(serializers.HyperlinkedModelSerializer):
	leagues = serializers.SerializerMethodField()

	class Meta:
		model = Location
		list_serializer_class = LocationSerializerList
		fields = ('id','name','leagues','priority','available')
	
	def get_leagues(self, obj):
		leagues = obj.leagues
		return MenuLeagueSerializer(leagues, many=True, context={'request': self.context['request']}).data

class LocationModifiedSerializer(serializers.HyperlinkedModelSerializer):
    location = serializers.SlugRelatedField(queryset = Location.objects.all(), slug_field='pk')
    store = serializers.SlugRelatedField(read_only=True, slug_field='pk')

    def create(self, validated_data):
        user = self.context['request'].user		
        league = validated_data.get('location')		
        location_modifieds = LocationModified.objects.filter(location__pk=league.pk, store=user.my_store)

        if location_modifieds:
            location_modifieds.update(**validated_data)
            return location_modifieds.first()

        instance = LocationModified(**validated_data)			
        instance.store = user.my_store		
        instance.save()
        return instance

    class Meta:
        model = LocationModified
        fields = ('location','priority','available','store')