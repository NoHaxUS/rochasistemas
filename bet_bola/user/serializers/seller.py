from rest_framework import serializers
from user.models import Manager, Seller, Punter
from core.models import Store

class SellerSerializer(serializers.HyperlinkedModelSerializer):	
	
	my_manager = serializers.SlugRelatedField(queryset=Manager.objects.all(), allow_null=True, slug_field='username')
	password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

	class Meta:
		model=Seller
		fields = ('id','username','first_name','password','cellphone','address','cpf','can_sell_unlimited','credit_limit','limit_time_to_cancel','my_manager','email')

	def create(self, validated_data):				
		obj = Seller(**validated_data)
		store = Store.objects.get(id=self.context['request'].GET.get('store'))
		obj.my_store=store
		obj.save()
		return obj

	def validate_email(self, value):
		if Seller.objects.filter(email=value):
			raise serializers.ValidationError("Email ja cadastrado.")
		return value
