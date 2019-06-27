from rest_framework import serializers
from user.models import Seller, Manager
from ticket.models import Ticket
from core.models import Store
from history.models import ManagerTransactions

class ManagerTransactionsSerializer(serializers.HyperlinkedModelSerializer):
	seller = serializers.SlugRelatedField(queryset = Seller.objects.all(),slug_field='first_name')
	manager = serializers.SlugRelatedField(queryset = Manager.objects.all(),slug_field='first_name')
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')
	transaction_date = serializers.DateTimeField(format='%d %B %Y', read_only=True)

	class Meta:
		model = ManagerTransactions
		fields = ('manager','seller','transaction_date','transferred_amount','manager_before_balance','manager_after_balance','seller_before_balance','seller_after_balance','store')