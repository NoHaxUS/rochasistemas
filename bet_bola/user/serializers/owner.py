from rest_framework import serializers
from user.models import TicketOwner
from core.models import Store

class OwnerSerializer(serializers.HyperlinkedModelSerializer):			
	
	class Meta:
		model=TicketOwner
		fields = ('first_name','cellphone')

	def create(self, validated_data):				
		obj = TicketOwner(**validated_data)		
		store = Store.objects.get(id=self.context['request'].GET.get('store'))
		obj.my_store=store
		obj.save()
		return obj