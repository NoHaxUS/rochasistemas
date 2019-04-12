from rest_framework import serializers
from core.models import Store
from .models import *


class PunterSerializer(serializers.HyperlinkedModelSerializer):	
	
	password = serializers.CharField(style={'input_type': 'password'})
	my_store = serializers.SlugRelatedField(read_only=True, slug_field='id')	

	class Meta:
		model=Punter
		fields = ('id','username','password','first_name', 'last_name', 'cellphone', 'email','my_store')


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


class SellerSerializer(serializers.HyperlinkedModelSerializer):	
	
	my_manager = serializers.SlugRelatedField(queryset=Manager.objects.all(), allow_null=True, slug_field='first_name')
	password = serializers.CharField(style={'input_type': 'password'})
	my_store = serializers.SlugRelatedField(read_only=True, slug_field='id')	

	class Meta:
		model=Seller
		fields = ('id','username','password','first_name', 'last_name', 'cpf','can_sell_unlimited','credit_limit','limit_time_to_cancel','my_manager','email','my_store')

	def create(self, validated_data):				
		obj = Seller(**validated_data)
		print("@@@@@@@")
		print(self.context['request'].GET.get('store'))
		store = Store.objects.get(id=self.context['request'].GET.get('store'))
		obj.my_store=store
		obj.save()
		return obj	

	def validate_email(self, value):
		if Punter.objects.filter(email=value):
			raise serializers.ValidationError("Email ja cadastrado.")
		return value


class NormalUserSerializer(serializers.HyperlinkedModelSerializer):		

	class Meta:
		model=NormalUser
		fields = ('id','first_name','cellphone')

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
		fields = ('id','username','password','first_name', 'last_name', 'cpf','cellphone','address', 'email','commission','credit_limit_to_add','can_cancel_ticket','limit_time_to_cancel','can_sell_unlimited','can_change_limit_time','based_on_profit','my_store')

	def create(self, validated_data):				
		obj = Manager(**validated_data)		
		store = Store.objects.get(id=self.context['request'].GET.get('store'))
		obj.my_store=store
		obj.save()
		return obj

	def validate_email(self, value):
		if Punter.objects.filter(email=value):
			raise serializers.ValidationError("Email ja cadastrado.")
		return value