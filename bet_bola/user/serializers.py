from rest_framework import serializers
from core.models import Store
from .models import *


class PunterSerializer(serializers.HyperlinkedModelSerializer):	

	my_store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')
	password = serializers.CharField(style={'input_type': 'password'})

	class Meta:
		model=Punter
		fields = ('username','password','first_name', 'last_name', 'cellphone', 'email','my_store')


class SellerSerializer(serializers.HyperlinkedModelSerializer):	
	
	my_manager = serializers.SlugRelatedField(read_only=True , slug_field='first_name')
	password = serializers.CharField(style={'input_type': 'password'})
	my_store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model=Seller
		fields = ('username','password','first_name', 'last_name', 'cpf','can_sell_unlimited','credit_limit','limit_time_to_cancel','my_manager', 'email','my_store')


class NormalUserSerializer(serializers.HyperlinkedModelSerializer):
	
	my_store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')	

	class Meta:
		model=Punter
		fields = ('first_name','cellphone','email','my_store')


class ManagerSerializer(serializers.HyperlinkedModelSerializer):	
	
	my_store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')
	password = serializers.CharField(style={'input_type': 'password'})

	class Meta:
		model = Manager
		fields = ('username','password','first_name', 'last_name', 'cpf','cellphone','address', 'email','commission','credit_limit_to_add','can_cancel_ticket','limit_time_to_cancel','can_sell_unlimited','can_change_limit_time','based_on_profit','my_store')
