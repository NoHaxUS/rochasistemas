from rest_framework import serializers
from user.models import Seller, Manager
from ticket.models import Ticket
from core.models import Store
from history.models import TicketValidationHistory

class TicketValidationSerializer(serializers.HyperlinkedModelSerializer):
    
	who_validated = serializers.SlugRelatedField(queryset = Seller.objects.all(),slug_field='first_name')
	ticket = serializers.SlugRelatedField(queryset = Ticket.objects.all(),slug_field='ticket_id')
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')		

	class Meta:
		model = TicketValidationHistory
		fields = ('who_validated','ticket','bet_value','date','who_validated','balance_before','balance_after','store')