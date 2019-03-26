from rest_framework import serializers
from core.models import Store
from .models import *


class PunterSerializer(serializers.HyperlinkedModelSerializer):	
	
	password = serializers.CharField(style={'input_type': 'password'})

	class Meta:
		model=Punter
		fields = ('username','password','first_name', 'last_name', 'cellphone', 'email')


	def create(self, validated_data):				
		obj = Punter.objects.create(**validated_data)		
		store = Store.objects.get(id=self.context['request'].GET.get('store'))
		obj.my_store=store
		obj.save()
		return obj


class SellerSerializer(serializers.HyperlinkedModelSerializer):	
	
	my_manager = serializers.SlugRelatedField(read_only=True , slug_field='first_name')
	password = serializers.CharField(style={'input_type': 'password'})	

	class Meta:
		model=Seller
		fields = ('username','password','first_name', 'last_name', 'cpf','can_sell_unlimited','credit_limit','limit_time_to_cancel','my_manager','email')

	def create(self, validated_data):				
		obj = Seller(**validated_data)
		store = Store.objects.get(id=self.context['request'].GET.get('store'))
		obj.my_store=store
		obj.save()
		return obj


class NormalUserSerializer(serializers.HyperlinkedModelSerializer):		

	class Meta:
		model=NormalUser
		fields = ('first_name','cellphone')

	def create(self, validated_data):				
		obj = NormalUser(**validated_data)		
		store = Store.objects.get(id=self.context['request'].GET.get('store'))
		obj.my_store=store
		obj.save()
		return obj


class ManagerSerializer(serializers.HyperlinkedModelSerializer):	
	
	my_store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')
	password = serializers.CharField(style={'input_type': 'password'})

	class Meta:
		model = Manager
		fields = ('username','password','first_name', 'last_name', 'cpf','cellphone','address', 'email','commission','credit_limit_to_add','can_cancel_ticket','limit_time_to_cancel','can_sell_unlimited','can_change_limit_time','based_on_profit','my_store')

	def create(self, validated_data):				
		obj = Manager(**validated_data)		
		store = Store.objects.get(id=self.context['request'].GET.get('store'))
		obj.my_store=store
		obj.save()
		return obj