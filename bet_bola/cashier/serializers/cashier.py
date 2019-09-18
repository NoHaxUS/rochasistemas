from django.db.models import Q, Count
from rest_framework import serializers
from rest_framework.response import Response
from ticket.serializers.reward import RewardSerializer, RewardSerializer
from ticket.serializers.payment import PaymentSerializerWithSeller, PaymentSerializer
from core.serializers.cotation import CotationTicketSerializer
from user.serializers.owner import OwnerSerializer
from ticket.paginations import TicketPagination
from utils.models import TicketCustomMessage
from utils import timezone as tzlocal
from ticket.models import Ticket
from user.models import TicketOwner
from user.models import CustomUser, Seller, Manager
from core.models import Store, Cotation
from decimal import Decimal
import datetime
import json


class CashierSerializer(serializers.HyperlinkedModelSerializer):
    payment = PaymentSerializerWithSeller()
    reward = RewardSerializer()
    creator = serializers.SlugRelatedField(read_only=True, slug_field='username')
    status = serializers.SerializerMethodField()
    comission = serializers.SerializerMethodField()
    bet_type = serializers.SerializerMethodField()
    manager = serializers.SerializerMethodField()
    won_bonus = serializers.SerializerMethodField()
    creation_date = serializers.DateTimeField(format='%d/%m/%Y %H:%M')
    cotations_count = serializers.SerializerMethodField()
    initialization_field = serializers.SerializerMethodField()
    closed_in_for_manager = serializers.SerializerMethodField()

    cotations_count_init = None
    user_type_init = None
    comissions_init = None
    entry_init = 0
    ticket_count = 0

    def get_closed_in_for_manager(self, obj):
        return obj.closed_in_for_manager

    def get_initialization_field(self, ticket):
        self.cotations_count_init = None
        if not self.cotations_count_init:
            self.cotations_count_init = ticket.cotations.count()

        if not self.comissions_init:
            self.comissions_init = ticket.payment.who_paid.seller.comissions
        if not self.user_type_init:
            self.user_type_init = ticket.payment.who_paid.user_type

    def get_cotations_count(self, obj):
        return self.cotations_count_init

    def get_won_bonus(self, obj):
        return obj.won_bonus()

    def get_status(self, obj):
        return obj.get_status_display()

    def get_comission(self, obj):
        if self.user_type_init == 2:
            key_value = {
                1:self.comissions_init.simple,
                2:self.comissions_init.double,
                3:self.comissions_init.triple,
                4:self.comissions_init.fourth,
                5:self.comissions_init.fifth,
                6:self.comissions_init.sixth
            }

            return Decimal(key_value.get(self.cotations_count_init, self.comissions_init.sixth_more) * obj.bet_value / 100)
        return Decimal(0)

    def get_bet_type(self, obj):

        key_value = {
            1:"simple",
            2:"double",
            3:"triple",
            4:"fourth",
            5:"fifth",
            6:"sixth"
        }
        return str(key_value.get(self.cotations_count_init, "sixth_more"))

    def get_manager(self, obj):
        if self.user_type_init == 2:
            manager = obj.payment.who_paid.seller.my_manager
            if manager:
                return {
                    "username": manager.username,
                    "comission_based_on_profit": manager.comission_based_on_profit
                }
        return None

    class Meta:
        model = Ticket
        fields = ('id','initialization_field','closed_in_for_manager','ticket_id','creation_date','creator','reward','won_bonus','cotations_count','bet_type','manager','comission','payment','bet_value','status')


class SellersCashierSerializer(serializers.HyperlinkedModelSerializer):
    initalization_field = serializers.SerializerMethodField()
    comission = serializers.SerializerMethodField()
    entry = serializers.SerializerMethodField()
    out = serializers.SerializerMethodField()
    won_bonus = serializers.SerializerMethodField()
    total_out = serializers.SerializerMethodField()
    profit = serializers.SerializerMethodField()

    seller_comission_init = 0
    out_value_init = 0
    entry_value_init = 0
    total_out_init = 0
    won_bonus_init = 0


    def get_initalization_field(self, seller):
        self.seller_comission_init = 0
        self.out_value_init = 0
        self.entry_value_init = 0
        self.total_out_init = 0
        self.won_bonus_init = 0

        tickets = Ticket.objects.filter(Q(payment__status=2, payment__who_paid__pk=seller.pk) &
        (Q(closed_in_for_seller=False) | Q(closed_out_for_seller=False, status__in=[4,2]))).exclude(Q(status__in=[5,6]) | Q(available=False))
        #.annotate(cotations_count=Count('cotations')).distinct()

        if self.context.get('request'):
            get = self.context['request'].GET
            post = self.context['request'].POST
            start_creation_date = None
            end_creation_date = None

            if get:
                start_creation_date = get.get('start_creation_date')
                end_creation_date = get.get('end_creation_date')
            elif post:
                data = json.loads(post.get('data'))
                start_creation_date = data.get('start_creation_date')
                end_creation_date = data.get('end_creation_date')

            if start_creation_date:
                start_creation_date = datetime.datetime.strptime(start_creation_date, '%d/%m/%Y').strftime('%Y-%m-%d')
                tickets = tickets.filter(creation_date__date__gte=start_creation_date)
            if end_creation_date:
                end_creation_date = datetime.datetime.strptime(end_creation_date, '%d/%m/%Y').strftime('%Y-%m-%d')
                tickets = tickets.filter(creation_date__date__lte=end_creation_date)

            seller_comission = seller.comissions

            for ticket in tickets:
                
                #calculating manager comission
                if not ticket.closed_in_for_seller:
                    seller_key = {
                        1:seller_comission.simple,
                        2:seller_comission.double,
                        3:seller_comission.triple,
                        4:seller_comission.fourth,
                        5:seller_comission.fifth,
                        6:seller_comission.sixth
                    }

                    # entry value
                    self.entry_value_init += ticket.bet_value

                    # seller comissions
                    self.seller_comission_init += seller_key.get(ticket.cotations.count(), seller_comission.sixth_more) * ticket.bet_value / 100
                    
                # calculating out value
                if ticket.status in [2,4]:
                    self.out_value_init += ticket.reward.value
                
                self.total_out_init = self.out_value_init + self.seller_comission_init

                # calculating won bonus
                if seller.my_store.my_configuration.bonus_won_ticket:
                    self.won_bonus_init += ticket.won_bonus()


    def get_comission(self, obj):
        return self.seller_comission_init

    def get_entry(self, obj):
        return self.entry_value_init

    def get_out(self, obj):
        return self.out_value_init

    def get_won_bonus(self, obj):
        return self.won_bonus_init

    def get_total_out(self, obj):
        return self.total_out_init
    
    def get_profit(self, obj):
        return self.get_entry(obj) - self.get_total_out(obj)


    class Meta:
        model = Seller
        fields = ('id','initalization_field','username','comission','entry','won_bonus','out','total_out','profit')


class ManagersCashierSerializer(serializers.HyperlinkedModelSerializer):
    initalization_field = serializers.SerializerMethodField()
    comission_seller = serializers.SerializerMethodField()
    comission = serializers.SerializerMethodField()
    entry = serializers.SerializerMethodField()
    out = serializers.SerializerMethodField()
    won_bonus = serializers.SerializerMethodField()
    total_out = serializers.SerializerMethodField()
    profit = serializers.SerializerMethodField()
    profit = serializers.SerializerMethodField()

    manager_comission_init = 0
    seller_comission_init = 0
    out_value_init = 0
    entry_value_init = 0
    total_out_init = 0
    won_bonus_init = 0
    profit_init = 0
    ticket_count = 0

    def get_initalization_field(self, manager):
        self.manager_comission_init = 0
        self.seller_comission_init = 0
        self.out_value_init = 0
        self.entry_value_init = 0
        self.total_out_init = 0
        self.won_bonus_init = 0
        self.profit_init = 0

        sellers = Seller.objects.filter(my_manager__pk=manager.pk, payment__status=2).distinct()

        for seller in sellers:
            tickets = Ticket.objects.filter(Q(payment__status=2, payment__who_paid__seller__pk=seller.pk) &
            (Q(closed_in_for_manager=False) | Q(closed_out_for_manager=False, status__in=[4,2])))\
            .exclude(Q(status__in=[5,6]) | Q(available=False))

            #self.ticket_count += tickets.count()
            #print(self.ticket_count)

            if self.context.get('request'):
                get = self.context['request'].GET
                post = self.context['request'].POST
                start_creation_date = None
                end_creation_date = None

                if get:
                    start_creation_date = get.get('start_creation_date')
                    end_creation_date = get.get('end_creation_date')
                elif post:
                    data = json.loads(post.get('data'))
                    start_creation_date = data.get('start_creation_date')
                    end_creation_date = data.get('end_creation_date')

                if start_creation_date:
                    start_creation_date = datetime.datetime.strptime(start_creation_date, '%d/%m/%Y').strftime('%Y-%m-%d')
                    tickets = tickets.filter(creation_date__date__gte=start_creation_date)
                if end_creation_date:
                    end_creation_date = datetime.datetime.strptime(end_creation_date, '%d/%m/%Y').strftime('%Y-%m-%d')
                    tickets = tickets.filter(creation_date__date__lte=end_creation_date)

            seller_comission = seller.comissions
            manager_comission = manager.comissions

            for ticket in tickets:
                #calculating manager comission
                if not ticket.closed_in_for_manager:
                #if True:
                    manager_key = {
                        1:manager_comission.simple,
                        2:manager_comission.double,
                        3:manager_comission.triple,
                        4:manager_comission.fourth,
                        5:manager_comission.fifth,
                        6:manager_comission.sixth
                    }

                    seller_key = {
                        1:seller_comission.simple,
                        2:seller_comission.double,
                        3:seller_comission.triple,
                        4:seller_comission.fourth,
                        5:seller_comission.fifth,
                        6:seller_comission.sixth
                    }

                    # manager comissions
                    self.manager_comission_init += manager_key.get(ticket.cotations.count(), manager_comission.sixth_more) * ticket.bet_value / 100

                    # seller comissions
                    self.seller_comission_init += seller_key.get(ticket.cotations.count(), seller_comission.sixth_more) * ticket.bet_value / 100
 
                    # entry value
                    self.entry_value_init += ticket.bet_value

                # calculating out value
                if ticket.status in [2,4]:
                    self.out_value_init += ticket.reward.value
            

                # calculating won bonus
                if manager.my_store.my_configuration.bonus_won_ticket:
                    self.won_bonus_init += ticket.won_bonus()

            # defining total out
            self.total_out_init = self.out_value_init + self.seller_comission_init

            # definig profit
            self.profit_init = self.entry_value_init - self.total_out_init
            
            # zero comission if manager is based on profit and profit is less than zero
            if manager.comission_based_on_profit and self.profit_init < 0:
                self.manager_comission_init = 0
            
            #print(seller, self.entry_value_init)


    def get_entry(self, obj):
        return self.entry_value_init

    def get_comission(self, obj):
        return self.manager_comission_init

    def get_out(self, obj):
        return self.out_value_init
    
    def get_won_bonus(self, obj):
        return self.won_bonus_init

    def get_total_out(self, obj):
        return self.total_out_init

    def get_comission_seller(self, obj):
        return self.seller_comission_init

    def get_profit(self, obj):
        return self.profit_init
    
    class Meta:
        model = Manager
        fields = ('id','initalization_field', 'username','comission','comission_seller','entry','won_bonus','out','total_out','profit')


class ManagerSpecificCashierSerializer(serializers.HyperlinkedModelSerializer):
    initalization_field = serializers.SerializerMethodField()
    comission = serializers.SerializerMethodField()
    comission_seller = serializers.SerializerMethodField()
    entry = serializers.SerializerMethodField()
    out = serializers.SerializerMethodField()
    profit = serializers.SerializerMethodField()
    won_bonus = serializers.SerializerMethodField()
    total_out = serializers.SerializerMethodField()

    manager_comission_init = 0
    seller_comission_init = 0
    out_value_init = 0
    won_bonus_init = 0
    total_out_init = 0
    entry_value_init = 0


    def get_initalization_field(self, seller):
        tickets = Ticket.objects.filter(Q(payment__status=2, payment__who_paid__pk=seller.pk) & 
        (Q(closed_in_for_manager=False) | Q(closed_out_for_manager=False, status__in=[4,2]))).exclude(Q(status__in=[5,6]) | Q(available=False))\
        #.annotate(cotations_count=Count('cotations')).distinct()

        if self.context.get('request'):
            start_creation_date = self.context['request'].GET.get('start_creation_date')
            end_creation_date = self.context['request'].GET.get('end_creation_date', None)

            if start_creation_date:
                start_creation_date = datetime.datetime.strptime(start_creation_date, '%d/%m/%Y').strftime('%Y-%m-%d')
                tickets = tickets.filter(creation_date__date__gte=start_creation_date)
            if end_creation_date:
                end_creation_date = datetime.datetime.strptime(end_creation_date, '%d/%m/%Y').strftime('%Y-%m-%d')
                tickets = tickets.filter(creation_date__date__lte=end_creation_date)
        
        manager = self.context['request'].user.manager
        manager_comission = manager.comissions
        seller_comission = seller.comissions

        for ticket in tickets:
            #calculating manager comission
            if not ticket.closed_in_for_manager:
                manager_key = {
                    1:manager_comission.simple,
                    2:manager_comission.double,
                    3:manager_comission.triple,
                    4:manager_comission.fourth,
                    5:manager_comission.fifth,
                    6:manager_comission.sixth
                }

                seller_key = {
                    1:seller_comission.simple,
                    2:seller_comission.double,
                    3:seller_comission.triple,
                    4:seller_comission.fourth,
                    5:seller_comission.fifth,
                    6:seller_comission.sixth
                }

                # manager comissions
                self.manager_comission_init += manager_key.get(ticket.cotations.count(), manager_comission.sixth_more) * ticket.bet_value / 100

                # seller comissions
                self.seller_comission_init += seller_key.get(ticket.cotations.count(), seller_comission.sixth_more) * ticket.bet_value / 100

                # entry value
                self.entry_value_init += ticket.bet_value

            # calculating out value
            if ticket.status in [2,4]:
                self.out_value_init += ticket.reward.value

            # calculating won bonus
            if manager.my_store.my_configuration.bonus_won_ticket:
                self.won_bonus_init += ticket.won_bonus()

        # defining total out
        self.total_out_init = self.out_value_init + self.seller_comission_init
        
        # definig profit
        self.profit_init = self.entry_value_init - self.total_out_init

        # zero comission if manager is based on profit and profit is less than zero
        if manager.comission_based_on_profit and self.profit_init < 0:
            self.manager_comission_init = 0


    def get_comission(self, obj):
        return self.manager_comission_init

    def get_comission_seller(self, obj):
        return self.seller_comission_init

    def get_entry(self, obj):
        return self.entry_value_init

    def get_out(self, obj):
        return self.out_value_init

    def get_won_bonus(self, obj):
        return self.won_bonus_init

    def get_total_out(self, obj):
        return self.total_out_init

    def get_profit(self, obj):
        return self.profit_init

    class Meta:
        model = Seller
        fields = ('id','initalization_field','username','comission','comission_seller','entry','won_bonus','out','total_out','profit')
