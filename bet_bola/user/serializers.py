from rest_framework import serializers
from core.models import Store
from .models import *


class PunterSerializer(serializers.HyperlinkedModelSerializer):	

	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model=Punter
		fields = ('username','first_name', 'last_name', 'cellphone', 'email','store')


class SellerSerializer(serializers.HyperlinkedModelSerializer):	
	
	my_manager = serializers.SlugRelatedField(read_only=True , slug_field='first_name')
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model=Seller
		fields = ('username','first_name', 'last_name', 'cpf','my_manager', 'email','store')


class NormalUserSerializer(serializers.HyperlinkedModelSerializer):
	
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model=Punter
		fields = ('first_name','email','store')


class ManagerSerializer(serializers.HyperlinkedModelSerializer):	
	
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model = Manager
		fields = ('username','first_name', 'last_name', 'cpf','cellphone','address', 'email','commission','credit_limit_to_add','can_cancel_ticket','limit_time_to_cancel','can_sell_unlimited','can_change_limit_time','based_on_profit','store')
