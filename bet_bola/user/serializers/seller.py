from rest_framework import serializers
from user.models import Manager, Seller, Punter
from core.models import Store
from django.utils.translation import gettext as _

class SellerSerializer(serializers.HyperlinkedModelSerializer):	
	
	my_manager = serializers.SlugRelatedField(queryset=Manager.objects.all(), allow_null=True, slug_field='username', error_messages={"does_not_exist": "{value} não existe."})
	password = serializers.CharField(style={'input_type': 'password'}, write_only=True)


	def create(self, validated_data):
		#REVISE
		#STORE IS STATIC
		store = Store.objects.get(pk=1)
		obj = Seller(**validated_data)
		obj.my_store=store
		obj.save()
		return obj
	

	def validate_email(self, value):
		if value:
			if Seller.objects.filter(email=value):
				raise serializers.ValidationError("Email ja cadastrado.")
			return value
		return value


	class Meta:
		model=Seller
		fields = ('id','username','first_name','password','cellphone','address','cpf','can_sell_unlimited','credit_limit','limit_time_to_cancel','my_manager','email','can_cancel_ticket')
