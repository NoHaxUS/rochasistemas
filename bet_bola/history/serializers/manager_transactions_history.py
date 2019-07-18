from rest_framework import serializers
from user.models import Seller, CustomUser
from ticket.models import Ticket
from core.models import Store
from history.models import ManagerTransactions

class ManagerTransactionsSerializer(serializers.HyperlinkedModelSerializer):
	user = serializers.SlugRelatedField(queryset = CustomUser.objects.filter(user_type__in=[2,3]),slug_field='username')
	creditor = serializers.SlugRelatedField(queryset = CustomUser.objects.filter(user_type__in=[3,4]), slug_field='username')
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')
	transaction_date = serializers.DateTimeField(read_only=True)

	class Meta:
		model = ManagerTransactions
		fields = ('creditor','user','transaction_date','transferred_amount','creditor_before_balance','creditor_after_balance','user_before_balance','user_after_balance','store')