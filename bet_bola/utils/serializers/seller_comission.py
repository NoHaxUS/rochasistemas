from rest_framework import serializers
from utils.models import SellerComission
from user.models import Seller

class SellerComissionSerializer(serializers.HyperlinkedModelSerializer):
	
	seller_related = serializers.SlugRelatedField(queryset = Seller.objects.all(), slug_field='first_name')


	def update(self, instance, validated_data):

		instance.simple = validated_data.get('simple', instance.simple)
		instance.double = validated_data.get('double', instance.double)
		instance.triple = validated_data.get('triple', instance.triple)
		instance.fourth = validated_data.get('fourth', instance.fourth)
		instance.fifth = validated_data.get('fifth', instance.fifth)
		instance.sixth = validated_data.get('sixth', instance.sixth)
		instance.sixth_more = validated_data.get('sixth_more', instance.sixth_more)
		instance.save()
		return instance


	def validate_simple(self, value):
		if value < 0 or value > 100:
			raise serializers.ValidationError('A Comissão não pode ser menor que 0 ou maior que 100')
		return value
	def validate_double(self, value):
		if value < 0 or value > 100:
			raise serializers.ValidationError('A Comissão não pode ser menor que 0 ou maior que 100')
		return value
	def validate_triple(self, value):
		if value < 0 or value > 100:
			raise serializers.ValidationError('A Comissão não pode ser menor que 0 ou maior que 100')
		return value
	def validate_fourth(self, value):
		if value < 0 or value > 100:
			raise serializers.ValidationError('A Comissão não pode ser menor que 0 ou maior que 100')
		return value
	def validate_fifth(self, value):
		if value < 0 or value > 100:
			raise serializers.ValidationError('A Comissão não pode ser menor que 0 ou maior que 100')
		return value
	def validate_sixth(self, value):
		if value < 0 or value > 100:
			raise serializers.ValidationError('A Comissão não pode ser menor que 0 ou maior que 100')
		return value
	def validate_sixth_more(self, value):
		if value < 0 or value > 100:
			raise serializers.ValidationError('A Comissão não pode ser menor que 0 ou maior que 100')
		return value


	class Meta:
		model = SellerComission
		fields = ('pk','seller_related','simple','double','triple','fourth','fifth','sixth','sixth_more')