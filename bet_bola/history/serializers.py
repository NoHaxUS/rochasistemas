from rest_framework import serializers
from user.models import Seller, Manager
from ticket.models import Ticket
from core.models import Store
from .models import *

class ManagerTransactionsSerializer(serializers.HyperlinkedModelSerializer):
	seller = serializers.SlugRelatedField(queryset = Seller.objects.all(),slug_field='first_name')
	manager = serializers.SlugRelatedField(queryset = Manager.objects.all(),slug_field='first_name')
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model = ManagerTransactions
		fields = ('manager','seller','transaction_date','transferred_amount','manager_before_balance','manager_after_balance','seller_before_balance','seller_after_balance','store')


class PunterPayedHistorySerializer(serializers.HyperlinkedModelSerializer):
	
	seller = serializers.SlugRelatedField(queryset = Seller.objects.all(),slug_field='first_name')	
	ticket_winner = serializers.SlugRelatedField(queryset = Ticket.objects.all(),slug_field='id')	
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')	

	class Meta:
		model = WinnerPaymentHistory
		fields = ('punter_payed','seller','ticket_winner','payment_date','payed_value','is_closed_for_seller','is_closed_for_manager','store')
