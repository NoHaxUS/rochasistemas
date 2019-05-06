from rest_framework import serializers
from core.models import Store
from user.models import Punter

class PunterSerializer(serializers.HyperlinkedModelSerializer):	
	
	password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
	my_store = serializers.SlugRelatedField(read_only=True, slug_field='id')	

	class Meta:
		model=Punter
		fields = ('id','username','password','first_name', 'cellphone', 'email','my_store')


	def create(self, validated_data):				
		obj = Punter(**validated_data)		
		store = Store.objects.get(id=self.context['request'].GET.get('store'))
		obj.my_store=store
		obj.save()
		return obj

	def validate_email(self, value):
		if Punter.objects.filter(email=value,my_store=self.context['request'].GET.get('store')):
			raise serializers.ValidationError("Email ja cadastrado.")
		return value