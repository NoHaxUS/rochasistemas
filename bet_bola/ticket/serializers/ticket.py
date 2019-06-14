
from rest_framework import serializers
from rest_framework.response import Response
from ticket.serializers.reward import RewardSerializer, RewardSerializer
from ticket.serializers.payment import PaymentSerializerWithSeller, PaymentSerializer
from core.serializers.cotation import CotationTicketSerializer
from user.serializers.owner import OwnerSerializer
from ticket.paginations import TicketPagination
from utils.models import TicketCustomMessage
from utils.utils import general_configurations
from utils import timezone as tzlocal
from ticket.models import Ticket
from user.models import TicketOwner
from user.models import CustomUser, Seller, Manager
from core.models import Store, Cotation
from decimal import Decimal
import datetime

class RevenueSerializer(serializers.HyperlinkedModelSerializer):
			
	payment = PaymentSerializerWithSeller()
	reward = RewardSerializer()	
	creator = serializers.SlugRelatedField(read_only=True, slug_field='username')
	status = serializers.SerializerMethodField()	
	comission = serializers.SerializerMethodField()	
	bet_type = serializers.SerializerMethodField()	
	manager = serializers.SerializerMethodField()
	won_bonus = serializers.SerializerMethodField()
	creation_date = serializers.DateTimeField(format='%d/%m/%Y %H:%M')


	class Meta:
		model = Ticket
		fields = ('id','creation_date','creator','reward','won_bonus','bet_type','manager','comission','payment','bet_value','status')

	
	def get_won_bonus(self, obj):
		return obj.won_bonus()

	def get_status(self, obj):		
		return obj.get_status_display()
	
	def get_comission(self, obj):		
		user_type = obj.payment.who_paid.user_type
		comission = None
		
		if user_type == 2:
			comission = obj.payment.who_paid.seller.comissions
			key_value = {1:comission.simple,2:comission.double,3:comission.triple,4:comission.fourth,5:comission.fifth,6:comission.sixth}				

			return str(float(key_value.get(obj.cotations.count(), comission.sixth_more) * obj.bet_value / 100))
		
		return "0.0"

	def get_bet_type(self, obj):
		key_value = {1:"simple",2:"double",3:"triple",4:"fourth",5:"fifth",6:"sixth"}
		return str(key_value.get(obj.cotations.count(), "sixth_more")) 				
	
	def get_manager(self, obj):		
		user_type = obj.payment.who_paid.user_type		
		if user_type == 2:
			manager = obj.payment.who_paid.seller.my_manager
			if manager:
				return {"username":manager.username,"comission_based_on_profit":manager.comission_based_on_profit}
		return None


class RevenueGeneralSellerSerializer(serializers.HyperlinkedModelSerializer):
	comission = serializers.SerializerMethodField()
	entry = serializers.SerializerMethodField()
	out = serializers.SerializerMethodField()
	won_bonus = serializers.SerializerMethodField()
	total_out = serializers.SerializerMethodField()

	class Meta:
		model = Seller
		fields = ('id','username','comission','entry','won_bonus','out','total_out')

	def get_ticket(self, obj):
		tickets = Ticket.objects.filter(payment__status=2, payment__who_paid__pk=obj.pk, closed_for_seller=False).exclude(status__in=[5,6])		
		start_creation_date = self.context['request'].GET.get('start_creation_date', None)
		end_creation_date = self.context['request'].GET.get('end_creation_date', None)

		if start_creation_date:		
			tickets = tickets.filter(creation_date__gte=start_creation_date)
		if end_creation_date:
			tickets = tickets.filter(creation_date__lte=end_creation_date)
		return tickets

	def get_comission(self, obj):				
		tickets = self.get_ticket(obj)
		comission = None
		value = 0
		for ticket in tickets:		
			comission = obj.comissions
			key_value = {1:comission.simple,2:comission.double,3:comission.triple,4:comission.fourth,5:comission.fifth,6:comission.sixth}				
			value += Decimal(key_value.get(ticket.cotations.count(), comission.sixth_more) * ticket.bet_value / 100)		
		return value

	def get_entry(self, obj):		
		tickets = self.get_ticket(obj)
		value = 0
		for ticket in tickets:					
			value += ticket.bet_value
		return value

	def get_out(self, obj):		
		tickets = self.get_ticket(obj).filter(status=2)		
		value = 0
		for ticket in tickets:							
			value += ticket.reward.value - ticket.won_bonus()
		return value
	
	def get_won_bonus(self, obj):		
		tickets = self.get_ticket(obj).filter(status=2)
		value = 0
		for ticket in tickets:					
			value += ticket.won_bonus()
		return value
	
	def get_total_out(self, obj):
		return self.get_won_bonus(obj) + self.get_out(obj) + self.get_comission(obj)


class RevenueGeneralManagerSerializer(RevenueGeneralSellerSerializer):
	comission_seller = serializers.SerializerMethodField()

	class Meta:
		model = Manager
		fields = ('id','username','comission','comission_seller','entry','won_bonus','out','total_out')

	def get_ticket(self, obj):				  	
		tickets = Ticket.objects.filter(payment__status=2, payment__who_paid__seller__my_manager__pk=obj.pk, closed_for_manager=False).exclude(status__in=[5,6])				
		start_creation_date = self.context['request'].GET.get('start_creation_date', None)
		end_creation_date = self.context['request'].GET.get('end_creation_date', None)

		if start_creation_date:		
			tickets = tickets.filter(creation_date__gte=start_creation_date)
		if end_creation_date:
			tickets = tickets.filter(creation_date__lte=end_creation_date)
		return tickets

	def get_comission(self, obj):				
		tickets = self.get_ticket(obj)
		comission = None
		value = 0
		for ticket in tickets:		
			comission = obj.comissions
			key_value = {1:comission.simple,2:comission.double,3:comission.triple,4:comission.fourth,5:comission.fifth,6:comission.sixth}				
			if obj.comission_based_on_profit:
				value += Decimal(key_value.get(ticket.cotations.count(), comission.profit_comission) * ticket.bet_value / 100)
			else:				
				value += Decimal(key_value.get(ticket.cotations.count(), comission.sixth_more) * ticket.bet_value / 100)		
		return value
	
	def get_comission_seller(self, obj):				
		tickets = self.get_ticket(obj)
		comission = None
		value = 0
		for ticket in tickets:
			user_type = ticket.payment.who_paid.user_type
			if user_type == 2:	
				comission = ticket.payment.who_paid.seller.comissions
				key_value = {1:comission.simple,2:comission.double,3:comission.triple,4:comission.fourth,5:comission.fifth,6:comission.sixth}
				value += Decimal(key_value.get(ticket.cotations.count(), comission.sixth_more) * ticket.bet_value / 100)		

		return value


class TicketSerializer(serializers.HyperlinkedModelSerializer):
	
	owner = serializers.SlugRelatedField(read_only=True,slug_field='first_name')
	creator = serializers.SlugRelatedField(read_only=True, slug_field='username')
	payment = PaymentSerializerWithSeller()
	reward = RewardSerializer()
	cotation_sum = serializers.SerializerMethodField()
	status = serializers.SerializerMethodField()
	cotations = CotationTicketSerializer(many=True)
	creation_date = serializers.DateTimeField(format='%d/%m/%Y %H:%M')


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
		store = self.context['request'].GET.get('store')
		my_store = Store.objects.get(pk=store)
		owner = TicketOwner.objects.create(my_store=my_store, **validated_data.pop('owner'))
		cotations = validated_data.pop('cotations')
		ticket = Ticket.objects.create(owner=owner, **validated_data)
		ticket.cotations.set(cotations)
		return ticket


	class Meta:
		model = Ticket
		fields = ('id','owner','creation_date','reward','cotations','payment','bet_value')


class TicketCustomMessageSerializer(serializers.HyperlinkedModelSerializer):

	store = serializers.SlugRelatedField(queryset = Store.objects.all(),slug_field='id')

	class Meta:
		model =  TicketCustomMessage
		fields = ('text','store')

