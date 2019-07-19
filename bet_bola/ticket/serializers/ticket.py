from rest_framework import serializers
from rest_framework.response import Response
from ticket.serializers.reward import RewardSerializer, RewardSerializer
from ticket.serializers.payment import PaymentSerializerWithSeller, PaymentSerializer
from core.serializers.cotation import CotationTicketSerializer, CotationTicketWithCopiedPriceSerializer
from user.serializers.owner import OwnerSerializer
from ticket.paginations import TicketPagination
from utils.models import TicketCustomMessage
from utils.models import GeneralConfigurations
from utils import timezone as tzlocal
from ticket.models import Ticket
from user.models import TicketOwner
from user.models import CustomUser, Seller, Manager
from core.models import Store, Cotation
from decimal import Decimal
import datetime
from utils.models import TicketCustomMessage


class ShowTicketSerializer(serializers.HyperlinkedModelSerializer):
	
	owner = serializers.SlugRelatedField(read_only=True,slug_field='first_name')
	creator = serializers.SerializerMethodField()
	payment = PaymentSerializerWithSeller()
	reward = RewardSerializer()
	cotation_sum = serializers.SerializerMethodField()
	status = serializers.SerializerMethodField()
	cotations = CotationTicketWithCopiedPriceSerializer(many=True)
	creation_date = serializers.DateTimeField(format='%d/%m/%Y %H:%M')
	ticket_message = serializers.SerializerMethodField()

	def get_creator(self, data):
		if data.creator:
			return {
				'name': data.creator.first_name,
				'user_type': data.creator.user_type
			}

	def get_ticket_message(self, data):
		request = self.context['request']
		store = Store.objects.get(pk=request.GET.get('store'))

		ticket_message = TicketCustomMessage.objects.filter(store=store).first()
		if ticket_message:
			return {
				'message': ticket_message.text
			}

	class Meta:
		model = Ticket
		fields = ('id','ticket_id','owner','creator','cotations',
		'cotation_sum','creation_date','reward','payment','bet_value','available','status','ticket_message')

	def get_cotation_sum(self, obj):
		return obj.cotation_sum()
	
	def get_status(self, obj):
		return obj.get_status_display()

class TicketSerializer(serializers.HyperlinkedModelSerializer):
	
	owner = serializers.SlugRelatedField(read_only=True,slug_field='first_name')
	creator = serializers.SerializerMethodField()
	payment = PaymentSerializerWithSeller()
	reward = RewardSerializer()
	cotation_sum = serializers.SerializerMethodField()
	status = serializers.SerializerMethodField()
	cotations = CotationTicketSerializer(many=True)
	creation_date = serializers.DateTimeField(format='%d/%m/%Y %H:%M')


	def get_creator(self, data):
		if data.creator:
			return {
				'name': data.creator.first_name,
				'user_type': data.creator.user_type
			}


	class Meta:
		model = Ticket
		fields = ('id','ticket_id','owner','creator','cotations','cotation_sum','creation_date','reward','payment','bet_value','available','status')

	def get_cotation_sum(self, obj):
		return obj.cotation_sum()
	
	def get_status(self, obj):
		return obj.get_status_display()



class CreateTicketSerializer(serializers.HyperlinkedModelSerializer):	
	owner = OwnerSerializer()
	creation_date = serializers.DateTimeField(read_only=True)
	payment = PaymentSerializer(read_only=True)	
	reward = RewardSerializer(read_only=True)
	cotations = serializers.PrimaryKeyRelatedField(many=True, queryset=Cotation.objects.all(), required=True)

	def create(self, validated_data):
		owner_serializer = OwnerSerializer(data=validated_data.pop('owner'), context=self.context)
		owner_serializer.is_valid()
		owner = owner_serializer.save()

		cotations = validated_data.pop('cotations')		
		ticket = Ticket.objects.create(owner=owner, **validated_data)
		ticket.cotations.set(cotations)
		return ticket

	def validate(self, data):
		store = self.context['request'].GET.get('store')
		user = self.context['request'].user
		if not user.is_anonymous and user.has_perm('user.be_admin'):
			raise serializers.ValidationError("Conta administradora não pode fazer aposta :)")

		if not user.is_anonymous and user.has_perm('user.be_manager'):
			raise serializers.ValidationError("Conta gerente não pode fazer aposta :)")

		try:
			config = GeneralConfigurations.objects.get(store=store)
			min_number_of_choices_per_bet = config.min_number_of_choices_per_bet
			max_number_of_choices_per_bet = config.max_number_of_choices_per_bet
			min_bet_value = config.min_bet_value
			max_bet_value = config.max_bet_value
			min_cotation_sum = config.min_cotation_sum
			max_cotation_sum = config.max_cotation_sum
			alert_bet_value = config.alert_bet_value

		except GeneralConfigurations.DoesNotExist:
			min_number_of_choices_per_bet = 1
			max_number_of_choices_per_bet = 1000
			min_bet_value = 0
			max_bet_value = 1000000
			min_cotation_sum = 0
			max_cotation_sum = 1000000
			alert_bet_value = 1500

		cotations_len = len(data['cotations'])
	
		cotation_mul = 1
		for cotation in data['cotations']:
			cotation_mul *= cotation.price
		
		cotation_mul = 0 if cotation_mul == 1 else cotation_mul

		if cotations_len < min_number_of_choices_per_bet:
			raise serializers.ValidationError("Você deve escolher pelo menos " + str(min_number_of_choices_per_bet) + "apostas.")
		
		if cotations_len > max_number_of_choices_per_bet :
			raise serializers.ValidationError("Você deve escolher no máximo " + str(max_number_of_choices_per_bet) + "apostas.")
		
		if data['bet_value'] < min_bet_value:
			raise serializers.ValidationError("O valor mínimo para apostas é R$ " + str(min_bet_value))

		if data['bet_value'] > max_bet_value:
			raise serializers.ValidationError("O valor máximo para apostas é R$ " + str(max_bet_value))
		
		if cotation_mul < min_cotation_sum:
			raise serializers.ValidationError("O valor da cotação total deve ser maior que "+ str(min_cotation_sum))
		
		if cotation_mul > cotation_mul:
			raise serializers.ValidationError("O valor da cotação total deve ser menor que "+ str(max_cotation_sum))
		 
		return data


	class Meta:
		model = Ticket
		fields = ('id','owner','creation_date','reward','cotations','payment','bet_value')


class TicketCustomMessageSerializer(serializers.HyperlinkedModelSerializer):

	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model =  TicketCustomMessage
		fields = ('text','store')

