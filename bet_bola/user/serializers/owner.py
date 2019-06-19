from rest_framework import serializers
from user.models import TicketOwner
from core.models import Store

class OwnerSerializer(serializers.HyperlinkedModelSerializer):			
	
	class Meta:
		model=TicketOwner
		fields = ('first_name','cellphone')

	def create(self, validated_data):
		request = self.context['request']
		store = Store.objects.get(pk=request.GET.get('store'))
		
		if request.user.has_perm('be_punter'):
			data = {
				'first_name': request.user.first_name,
				'cellphone': request.user.cellphone
			}
			obj = TicketOwner(**data)
		else:
			obj = TicketOwner(**validated_data)
		
		obj.my_store=store
		obj.save()
		return obj