from rest_framework import serializers
from user.models import Seller
from ticket.models import Ticket
from core.models import Store
from history.models import TicketCancelationHistory


class TicketCancelationSerializer(serializers.HyperlinkedModelSerializer):
    
	ticket = serializers.SlugRelatedField(queryset = Ticket.objects.all(),slug_field='ticket_id')
	who_cancelled = serializers.SlugRelatedField(queryset = Seller.objects.all(),slug_field='first_name')	
	who_paid = serializers.SlugRelatedField(queryset = Seller.objects.all(),slug_field='first_name')	
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')
	date = serializers.DateTimeField(format='%d %B %Y', read_only=True)	

	class Meta:
		model = TicketCancelationHistory
		fields = ('who_cancelled','ticket','date','who_paid','store')