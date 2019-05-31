from rest_framework import serializers
from user.models import Manager, Seller, Punter
from core.models import Store
from django.utils.translation import gettext as _

class SellerSerializer(serializers.HyperlinkedModelSerializer):	
	
	my_manager = serializers.SlugRelatedField(queryset=Manager.objects.all(), allow_null=True, slug_field='username', error_messages={"does_not_exist": "{value} não existe."})
	password = serializers.CharField(style={'input_type': 'password'}, write_only=True, allow_null=True)


	def create(self, validated_data):
		#REVISE
		#STORE IS STATIC
		store = Store.objects.get(pk=1)
		obj = Seller(**validated_data)
		obj.my_store=store
		obj.save()
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
		
		manager_username = validated_data.get('my_manager', None)
		if manager_username:
			manager_instance = Manager.objects.filter(username=manager_username).first()
			if manager_instance:
				instance.my_manager = manager_instance
			else:
				serializers.ValidationError("O gerente informado não existe.")
		
		instance.email = validated_data.get('email', instance.email)
		instance.can_cancel_ticket = validated_data.get('can_cancel_ticket', instance.can_cancel_ticket)
		instance.limit_time_to_cancel = validated_data.get('limit_time_to_cancel', instance.limit_time_to_cancel)
		instance.can_sell_unlimited = validated_data.get('can_sell_unlimited', instance.can_sell_unlimited)
		
		instance.save()
		return instance

	


	def validate_email(self, value):
		if self.context['request'].method == 'POST' and value:
			if Seller.objects.filter(email=value):
				raise serializers.ValidationError("Email já cadastrado.")
			return value
		return value


	class Meta:
		model=Seller
		fields = ('id','username','first_name','password','cellphone','address','cpf','can_sell_unlimited','credit_limit','limit_time_to_cancel','my_manager','email','can_cancel_ticket')
