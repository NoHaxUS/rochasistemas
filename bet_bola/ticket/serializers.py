from rest_framework import serializers, status
from core.serializers import CotationSerializer,CotationTicketSerializer
from user.models import Seller, Manager,CustomUser
from core.models import Store, Cotation
from user.serializers import NormalUserSerializer, PunterSerializer, SellerSerializer
from utils.utils import general_configurations
from utils import timezone as tzlocal
from .models import *

class TicketSerializer(serializers.HyperlinkedModelSerializer):

	seller = serializers.SlugRelatedField(queryset = CustomUser.objects.all(),slug_field='first_name')
	user = serializers.SlugRelatedField(queryset = CustomUser.objects.all(),slug_field='first_name')
	normal_user = serializers.SlugRelatedField(queryset = CustomUser.objects.all(),slug_field='first_name')
	payment = serializers.SlugRelatedField(queryset = Payment.objects.all(),slug_field='status_payment')
	reward = serializers.SlugRelatedField(queryset = Reward.objects.all(),slug_field='id')
	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')
	ticket_status = serializers.SerializerMethodField()
	cotations = CotationTicketSerializer(many=True)

	class Meta:
		model = Ticket
		fields = ('id','user','seller','normal_user','cotations','creation_date','reward','payment','value','visible','ticket_status','store')

	def get_ticket_status(self, obj):
		return obj.ticket_status
	



class RewardSerializer(serializers.HyperlinkedModelSerializer):
	who_rewarded = serializers.SlugRelatedField(queryset = Seller.objects.all(),slug_field='first_name')

	class Meta:
		model = Reward
		fields = ('who_rewarded','reward_date','reward_status')


class PaymentSerializer(serializers.HyperlinkedModelSerializer):

	who_set_payment = SellerSerializer(read_only=True)

	class Meta:
		model = Payment
		fields =  ('who_set_payment','status_payment','payment_date','seller_was_rewarded','manager_was_rewarded')


#EXTRA SERIALIZERS

class CreateTicketAnonymousUserSerializer(serializers.HyperlinkedModelSerializer):	
	normal_user = NormalUserSerializer()
	creation_date = serializers.DateTimeField(read_only=True)	
	payment = PaymentSerializer(read_only=True)	
	reward = serializers.SlugRelatedField(read_only=True, slug_field='reward_status')	
	cotations = serializers.PrimaryKeyRelatedField(many=True,queryset=Cotation.objects.filter(game__id__in=[80053039]), required=True)	

	def update(self, instance, validated_data):
		normal_user = validated_data.pop('normal_user')		
		value = validated_data.pop('value')		
		visible = validated_data.pop('visible')
		cotations = validated_data.pop('cotations')		
		cotation_ids = [cotation.id for cotation in cotations]

		ticket = Ticket.objects.get(id=str(instance))
		ticket.value = value
		ticket.visible = visible
		ticket.cotations.clear()

		for cotation in  Cotation.objects.in_bulk(cotation_ids):
			ticket.cotations.add(cotation)
		

		ticket.save()			
		return ticket
		

	def validate_value(self, value):
		store = self.context['request'].GET.get('store')
		configurations = general_configurations(store)
		
		if value < configurations["min_bet_value"]:
			if value <= 0:	                       
				raise serializers.ValidationError("Valor da aposta inválido.")	        	       
			raise serializers.ValidationError("A aposta mínima é: R$ " + str(configurations["min_bet_value"]))	
		elif value > configurations["max_bet_value"]:
			raise serializers.ValidationError("A aposta ultrapassou o valor maximo de R$ " + str(configurations["max_bet_value"]))
		return value	

	def validate_cotations(self, cotations):
		store = self.context['request'].GET.get('store')		
		game_list = [cotation.game for cotation in cotations]
		configurations = general_configurations(store)		
		
		if len(cotations) < configurations["min_number_of_choices_per_bet"]:			
			raise serializers.ValidationError("Desculpe, Aposte em pelo menos " + str(configurations["min_number_of_choices_per_bet"]) + " jogo.")
		
		if len(cotations) > configurations["max_number_of_choices_per_bet"]:			
			raise serializers.ValidationError("Desculpe, O número máximo de " + str(configurations["max_number_of_choices_per_bet"]) + " apostas por bilhete foi excedido.")

		if game_list.__len__() != list(set(game_list)).__len__():
			raise serializers.ValidationError("Desculpe, não é permitido mais de uma aposta no mesmo jogo.")

		for cotation in cotations:								
			try:													
				if cotation.game.start_date < tzlocal.now():														
					raise serializers.ValidationError("Desculpe, o jogo " + cotation.game.name + " já começou, remova-o")
			except Cotation.DoesNotExist:				
				raise serializers.ValidationError("Erro, uma das cotas enviadas não existe.")	

		return cotations

	class Meta:
		model = Ticket
		fields = ('id','normal_user','creation_date','reward','cotations','payment','value','visible')


class CreateTicketLoggedUserSerializer(CreateTicketAnonymousUserSerializer):	

	def __init__(self, *args, **kwargs):
		super(CreateTicketLoggedUserSerializer, self).__init__(*args, **kwargs)
		request = kwargs['context']['request']		
		if request.user.has_perm('user.be_punter'):			
			self.fields['normal_user'] = NormalUserSerializer(read_only=True)

	class Meta:
		model = Ticket
		fields = ('id','normal_user','creation_date','reward','cotations','payment','value','visible')

