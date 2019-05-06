from rest_framework import serializers
from core.models import Store
from user.models import Manager

class ManagerSerializer(serializers.HyperlinkedModelSerializer):	
	
	my_store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')
	password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

	class Meta:
		model = Manager
		fields = ('id','username','first_name','password','cpf','cellphone','address', 'email','commission','credit_limit_to_add','can_cancel_ticket','limit_time_to_cancel','can_sell_unlimited','can_change_limit_time','based_on_profit','my_store')

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