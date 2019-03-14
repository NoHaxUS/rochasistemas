from rest_framework import serializers
from core.serializers import CotationSerializers
from user.models import Seller, Manager,CustomUser
from core.models import Store
from .models import *

class TicketSerializer(serializers.HyperLinkedModelSerializer):

	seller = serializers.SlugRelatedField(queryset = CustomUser.objects.all(),slug_field='first_name')
	normal_user = serializers.SlugRelatedField(queryset = CustomUser.objects.all(),slug_field='first_name')
	payment = serializers.SlugRelatedField(queryset = Payment.objects.all(),slug_field='status_payment')
	reward = serializers.SlugRelatedField(queryset = Reward.objects.all(),slug_field='value')
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')
	cotations = CotationSerializers(many=True)

	class Meta:
		model = Ticket
		fields = ('seller','normal_user','cotations','creation_date','reward','payment','value','visible','store')


class RewardSerializer(serializers.HyperLinkedModelSerializer):
	who_rewarded = serializers.SlugRelatedField(queryset = Seller.objects.all(),slug_field='first_name')

	class Meta:
		model = Reward
		fields = ('who_rewarded','reward_date','reward_status')


class Payment(serializers.HyperLinkedModelSerializer):

	who_set_payment = serializers.SlugRelatedField(queryset = Seller.objects.all(),slug_field='first_name')

	class Meta:
		model = Payment
		fields =  ('who_set_payment','status_payment','payment_date','seller_was_rewarded','manager_was_reward')