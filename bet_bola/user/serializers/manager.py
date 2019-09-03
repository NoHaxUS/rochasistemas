from rest_framework import serializers
from core.models import Store
from user.models import Manager
from utils.models import ManagerComission

class ManagerSerializer(serializers.HyperlinkedModelSerializer):
	password = serializers.CharField(style={'input_type': 'password'}, write_only=True, allow_null=True)

	class Meta:
		model = Manager
		fields = ('id','username','first_name','password','cpf','cellphone','address', 'email','can_cancel_ticket','can_modify_seller','can_modify_seller_comissions','limit_time_to_cancel','can_sell_unlimited','credit_limit','can_change_limit_time','comission_based_on_profit')

	def create(self, validated_data):				
		obj = Manager(**validated_data)		
		store = self.context['request'].user.my_store
		obj.my_store=store
		obj.save()

		ManagerComission.objects.create(
			manager_related=obj,
			store=store
		)
		return obj


	def update(self, instance, validated_data):
		instance.username = validated_data.get('username', instance.username)
		password = validated_data.get('password', instance.password)
		if password:
			instance.password = password
		instance.first_name = validated_data.get('first_name', instance.first_name)
		instance.cellphone = validated_data.get('cellphone', instance.cellphone)
		instance.address = validated_data.get('address', instance.address)
		instance.cpf = validated_data.get('cpf', instance.cpf)
		instance.email = validated_data.get('email', instance.email)
		instance.can_cancel_ticket = validated_data.get('can_cancel_ticket', instance.can_cancel_ticket)
		instance.limit_time_to_cancel = validated_data.get('limit_time_to_cancel', instance.limit_time_to_cancel)
		instance.can_sell_unlimited = validated_data.get('can_sell_unlimited', instance.can_sell_unlimited)
		instance.can_modify_seller_comissions = validated_data.get('can_modify_seller_comissions', instance.can_modify_seller_comissions)
		instance.can_modify_seller = validated_data.get('can_modify_seller', instance.can_modify_seller)
		instance.can_change_limit_time = validated_data.get('can_change_limit_time', instance.can_change_limit_time)
		instance.comission_based_on_profit = validated_data.get('comission_based_on_profit', instance.comission_based_on_profit)

		instance.save()
		return instance

	def validate_email(self, value):
		if self.context['request'].method == 'POST' and value:
			if Manager.objects.filter(email=value):
				raise serializers.ValidationError("Email já cadastrado.")
			return value
		return value