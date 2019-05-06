from rest_framework import serializers
from utils.models import Comission
from user.models import Seller

class ComissionSerializer(serializers.HyperlinkedModelSerializer):
	
	seller_related = serializers.SlugRelatedField(queryset = Seller.objects.all(),slug_field='first_name')

	class Meta:
		model = Comission
		fields = ('seller_related','simple','double','triple','fourth','fifth','sixth','sixth_more')

	def validate(self, data):
		if data['simple'] < 0 or data['simple'] > 100:
			raise serializers.ValidationError('Comissão não pode ser menor que 0 ou maior que 100')
		if data['double'] < 0 or data['double'] > 100:
			raise serializers.ValidationError('Comissão não pode ser menor que 0 ou maior que 100')
		if data['triple'] < 0 or data['triple'] > 100:
			raise serializers.ValidationError('Comissão não pode ser menor que 0 ou maior que 100')
		if data['fourth'] < 0 or data['fourth'] > 100:
			raise serializers.ValidationError('Comissão não pode ser menor que 0 ou maior que 100')
		if data['fifth'] < 0 or data['fifth'] > 100:
			raise serializers.ValidationError('Comissão não pode ser menor que 0 ou maior que 100')
		if data['sixth'] < 0 or data['sixth'] > 100:
			raise serializers.ValidationError('Comissão não pode ser menor que 0 ou maior que 100')
		if data['sixth_more'] < 0 or data['sixth_more'] > 100:
			raise serializers.ValidationError('Comissão não pode ser menor que 0 ou maior que 100')