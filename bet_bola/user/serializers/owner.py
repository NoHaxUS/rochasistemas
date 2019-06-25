from rest_framework import serializers
from user.models import TicketOwner
from core.models import Store

class OwnerSerializer(serializers.HyperlinkedModelSerializer):

	def create(self, validated_data):
		request = self.context['request']
		store = Store.objects.get(pk=request.GET.get('store'))
		
		if request.user.has_perm('user.be_punter'):
			data = {
				'first_name': request.user.first_name,
				'cellphone': request.user.cellphone
			}
			obj = TicketOwner.objects.create(my_store=store, **data)
		else:
			obj = TicketOwner.objects.create(my_store=store, **validated_data)
		
		return obj

	class Meta:
		model=TicketOwner
		fields = ('first_name','cellphone')