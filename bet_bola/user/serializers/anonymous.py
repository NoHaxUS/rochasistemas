from rest_framework import serializers
from user.models import AnonymousUser
from core.models import Store

class AnonymousUserSerializer(serializers.HyperlinkedModelSerializer):			
	
	class Meta:
		model=AnonymousUser
		fields = ('id','first_name','cellphone')

	def create(self, validated_data):				
		obj = AnonymousUser(**validated_data)		
		store = Store.objects.get(id=self.context['request'].GET.get('store'))
		obj.my_store=store
		obj.save()
		return obj