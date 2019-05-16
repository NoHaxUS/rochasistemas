from rest_framework import serializers
from user.models import Seller, Manager
from ticket.models import Ticket
from core.models import Store
from .models import *

class SellerSalesHistorySerializer(serializers.HyperlinkedModelSerializer):

	seller = serializers.SlugRelatedField(queryset = Seller.objects.all(),slug_field='first_name')
	bet_ticket = serializers.SlugRelatedField(queryset = Ticket.objects.all(),slug_field='id')
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model = TicketValidationHistory
		fields = ('seller','bet_ticket','sell_date','value','seller_before_balance','seller_after_balance','store')


class ManagerTransactionsSerializer(serializers.HyperlinkedModelSerializer):
	seller = serializers.SlugRelatedField(queryset = Seller.objects.all(),slug_field='first_name')
	manager = serializers.SlugRelatedField(queryset = Manager.objects.all(),slug_field='first_name')
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model = ManagerTransactions
		fields = ('manager','seller','transaction_date','transferred_amount','manager_before_balance','manager_after_balance','seller_before_balance','seller_after_balance','store')


class RevenueHistorySellerSerializer(serializers.HyperlinkedModelSerializer):
	
	seller = serializers.SlugRelatedField(queryset = Seller.objects.all(),slug_field='first_name')
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')	

	class Meta:
		model = RevenueHistorySeller
		fields = ('who_reseted_revenue','seller','revenue_reseted_date','final_revenue','earned_value','final_out_value','profit','store')


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
		model = PunterPayedHistory
		fields = ('punter_payed','seller','ticket_winner','payment_date','payed_value','is_closed_for_seller','is_closed_for_manager','store')


class TicketCancelationHistorySerializer(serializers.HyperlinkedModelSerializer):

	ticket_cancelled = serializers.SlugRelatedField(queryset = Ticket.objects.all(),slug_field='id')
	seller_of_payed = serializers.SlugRelatedField(queryset = Seller.objects.all(),slug_field='first_name')	
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')	

	class Meta:
		model = TicketCancelationHistory
		fields = ('who_cancelled','ticket_cancelled','cancelation_date','seller_of_payed','store')