from rest_framework import serializers
from user.models import Seller, Manager
from ticket.models import Ticket
from core.models import Store
from .models import *

class SellerSalesHistorySerializer(serializers.HyperlinkedModelSerializer):

	who_validated = serializers.SlugRelatedField(queryset = Seller.objects.all(),slug_field='first_name')
	ticket = serializers.SlugRelatedField(queryset = Ticket.objects.all(),slug_field='ticket_id')
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')
	date = serializers.DateTimeField(format='%d %B %Y', read_only=True)	

	class Meta:
		model = TicketValidationHistory
		fields = ('who_validated','ticket','bet_value','date','who_validated','balance_before','balance_after','store')


class ManagerTransactionsSerializer(serializers.HyperlinkedModelSerializer):
	seller = serializers.SlugRelatedField(queryset = Seller.objects.all(),slug_field='first_name')
	manager = serializers.SlugRelatedField(queryset = Manager.objects.all(),slug_field='first_name')
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model = ManagerTransactions
		fields = ('manager','seller','transaction_date','transferred_amount','manager_before_balance','manager_after_balance','seller_before_balance','seller_after_balance','store')





class RevenueHistoryManagerSerializer(serializers.HyperlinkedModelSerializer):

	manager = serializers.SlugRelatedField(queryset = Manager.objects.all(),slug_field='first_name')
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')	

	class Meta:
		model = RevenueHistoryManager
		fields = ('who_reseted_revenue','manager','revenue_reseted_date','final_revenue','actual_comission','earned_value','final_out_value','profit','store')


class PunterPayedHistorySerializer(serializers.HyperlinkedModelSerializer):
	
	seller = serializers.SlugRelatedField(queryset = Seller.objects.all(),slug_field='first_name')	
	ticket_winner = serializers.SlugRelatedField(queryset = Ticket.objects.all(),slug_field='id')	
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')	

	class Meta:
		model = WinnerPaymentHistory
		fields = ('punter_payed','seller','ticket_winner','payment_date','payed_value','is_closed_for_seller','is_closed_for_manager','store')


class TicketCancelationHistorySerializer(serializers.HyperlinkedModelSerializer):

	ticket = serializers.SlugRelatedField(queryset = Ticket.objects.all(),slug_field='ticket_id')
	who_cancelled = serializers.SlugRelatedField(queryset = Seller.objects.all(),slug_field='first_name')	
	who_paid = serializers.SlugRelatedField(queryset = Seller.objects.all(),slug_field='first_name')	
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')
	date = serializers.DateTimeField(format='%d %B %Y', read_only=True)	

	class Meta:
		model = TicketCancelationHistory
		fields = ('who_cancelled','ticket','date','who_paid','store')