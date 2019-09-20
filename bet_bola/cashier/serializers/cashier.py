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

class ManagerCashierSerializer(serializers.HyperlinkedModelSerializer):
    initialization_field = serializers.SerializerMethodField()
    entry = serializers.SerializerMethodField()
    comission = serializers.SerializerMethodField()
    out = serializers.SerializerMethodField()
    won_bonus = serializers.SerializerMethodField()
    total_out = serializers.SerializerMethodField()
    profit = serializers.SerializerMethodField()
    tickets = serializers.SerializerMethodField()
    seller_comission = serializers.SerializerMethodField()

    entry_value_init = 0
    comission_init = 0
    seller_comission_init = 0
    out_value_init = 0
    won_bonus_init = 0
    total_out_init = 0
    profit_init = 0
    tickets_init = []

    def get_initialization_field(self, user):
        self.tickets_init = []
        
        if user.user_type == 3:            
            tickets = Ticket.objects.filter(Q(payment__status=2, payment__who_paid__seller__my_manager__pk=user.pk, store=user.my_store) & 
            (Q(closed_in_for_manager=False) | Q(closed_out_for_manager=False, status__in=[4,2]))).distinct().exclude(Q(status__in=[5,6]) | Q(available=False)).order_by('-creation_date')

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
                        
            manager_comission = user.manager.comissions

            manager_key = {
                        1:manager_comission.simple,
                        2:manager_comission.double,
                        3:manager_comission.triple,
                        4:manager_comission.fourth,
                        5:manager_comission.fifth,
                        6:manager_comission.sixth
                    }
            
            for ticket in tickets:                
                self.tickets_init.append({
                    'ticket_id':ticket.ticket_id,
                    'status':ticket.get_status_display(),
                    'won_bonus':ticket.won_bonus(),
                    'bet_value': ticket.bet_value,
                    'cotations_count': ticket.cotations.count(),
                    'payment':{'who_paid':ticket.payment.who_paid.username},
                    'reward':{'value':ticket.reward.value},
                    'creation_date':ticket.creation_date
                    })
                
                if not ticket.closed_in_for_manager:                    
                    seller_comission = ticket.payment.who_paid.seller.comissions
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

                    self.comission_init += manager_key.get(ticket.cotations.count(), manager_comission.sixth_more) * ticket.bet_value / 100

                    self.seller_comission_init += seller_key.get(ticket.cotations.count(), seller_comission.sixth_more) * ticket.bet_value / 100
                
                if ticket.status in [2,4]:
                    self.out_value_init += ticket.reward.value
                                
                # calculating won bonus
                if user.my_store.my_configuration.bonus_won_ticket:
                    self.won_bonus_init += ticket.won_bonus()                        

            self.total_out_init = self.out_value_init + self.seller_comission_init

            self.profit_init = self.entry_value_init - self.total_out_init

            if user.manager.comission_based_on_profit and self.profit_init < 0:
                self.comission_init = 0
            elif user.manager.comission_based_on_profit:                
                self.comission_init = self.profit_init * user.manager.comissions.profit_comission / 100

            self.profit_init -= self.comission_init
            
    def get_entry(self, user):
        return self.entry_value_init

    def get_out(self, user):
        return self.out_value_init

    def get_total_out(self, user):
        return self.total_out_init

    def get_won_bonus(self, user):
        return self.won_bonus_init
        
    def get_comission(self, user):
        return self.comission_init
    
    def get_seller_comission(self, user):
        return self.seller_comission_init

    def get_profit(self, user):
        return self.profit_init
    
    def get_tickets(self, user):        
        return self.tickets_init

    class Meta:
        model = CustomUser
        fields = ('id','initialization_field','entry','out','total_out','won_bonus','comission','seller_comission','profit','tickets')


class SellerCashierSerializer(serializers.HyperlinkedModelSerializer):
    initialization_field = serializers.SerializerMethodField()
    entry = serializers.SerializerMethodField()
    comission = serializers.SerializerMethodField()
    out = serializers.SerializerMethodField()
    won_bonus = serializers.SerializerMethodField()
    total_out = serializers.SerializerMethodField()
    profit = serializers.SerializerMethodField()
    tickets = serializers.SerializerMethodField()

    entry_value_init = 0
    comission_init = 0    
    out_value_init = 0
    won_bonus_init = 0
    total_out_init = 0
    profit_init = 0
    tickets_init = []

    def get_initialization_field(self, user):
        self.tickets_init = []
        tickets = Ticket.objects.none()
        if user.user_type == 2:
            tickets = Ticket.objects.filter(Q(payment__status=2, payment__who_paid__pk=user.pk, store=user.my_store) & 
            (Q(closed_in_for_seller=False) | Q(closed_out_for_seller=False, status__in=[4,2]))).exclude(Q(status__in=[5,6]) | Q(available=False)).distinct().order_by('-creation_date','ticket_id')

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
            
            seller_comission = user.seller.comissions
            seller_key = {
                        1:seller_comission.simple,
                        2:seller_comission.double,
                        3:seller_comission.triple,
                        4:seller_comission.fourth,
                        5:seller_comission.fifth,
                        6:seller_comission.sixth
                    }

            for ticket in tickets:                                
                if not ticket.closed_in_for_seller:                                                           
                    # entry value
                    self.entry_value_init += ticket.bet_value

                    # seller comissions
                    comission_temp = seller_key.get(ticket.cotations.count(), seller_comission.sixth_more) * ticket.bet_value / 100
                    self.comission_init += comission_temp

                if ticket.status in [2,4]:
                    self.out_value_init += ticket.reward.value                

                # calculating won bonus
                if user.my_store.my_configuration.bonus_won_ticket:
                    self.won_bonus_init += ticket.won_bonus()
                
                self.tickets_init.append({
                    'ticket_id':ticket.ticket_id,
                    'status':ticket.get_status_display(),
                    'comission':comission_temp,
                    'won_bonus':ticket.won_bonus(),
                    'bet_value': ticket.bet_value,
                    'cotations_count': ticket.cotations.count(),
                    'reward':{'value':ticket.reward.value},
                    'creation_date':ticket.creation_date
                    })
            
            self.total_out_init = self.out_value_init + self.comission_init

            self.profit_init = self.entry_value_init - self.total_out_init

        
    def get_entry(self, user):
        return self.entry_value_init

    def get_out(self, user):
        return self.out_value_init

    def get_total_out(self, user):
        return self.total_out_init

    def get_won_bonus(self, user):
        return self.won_bonus_init
        
    def get_comission(self, user):
        return self.comission_init        

    def get_profit(self, user):
        return self.profit_init
    
    def get_tickets(self, user):        
        return self.tickets_init

    class Meta:
        model = CustomUser
        fields = ('id','initialization_field','entry','out','total_out','won_bonus','comission','profit','tickets')        


class SellerCashierListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = super().to_representation(data)
        cashier_results = {
            'entry':self.child.entry_value_end,
            'out':self.child.out_value_end,
            'won_bonus':self.child.won_bonus_end,
            'comission':self.child.comission_end,
            'total_out':self.child.total_out_end,
            'profit': self.child.entry_value_end - self.child.total_out_end,
            'data':data
        }
        
        return [cashier_results]


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

    comission_end = 0
    out_value_end = 0
    entry_value_end = 0
    total_out_end = 0
    won_bonus_end = 0    

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
            
            self.entry_value_end += self.entry_value_init
            self.won_bonus_end += self.won_bonus_init
            self.out_value_end += self.out_value_init
            self.total_out_end += self.total_out_init
            self.comission_end += self.seller_comission_init            

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
        list_serializer_class = SellerCashierListSerializer
        fields = ('id','initalization_field','username','comission','entry','won_bonus','out','total_out','profit')


class ManagerCashierListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = super().to_representation(data)
        cashier_results = {
            'entry':self.child.entry_value_end,
            'out':self.child.out_value_end,
            'won_bonus':self.child.won_bonus_end,
            'comission':self.child.comission_end,
            'seller_comission':self.child.seller_comission_end,
            'total_out':self.child.total_out_end,
            'profit': self.child.entry_value_end - self.child.total_out_end,
            'data':data
        }        
        return [cashier_results]


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

    comission_end = 0
    seller_comission_end = 0
    out_value_end = 0
    entry_value_end = 0
    total_out_end = 0
    won_bonus_end = 0    

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
            
        self.entry_value_end += self.entry_value_init
        self.won_bonus_end += self.won_bonus_init
        self.out_value_end += self.out_value_init
        self.total_out_end += self.total_out_init
        self.comission_end += self.manager_comission_init
        self.seller_comission_end += self.seller_comission_init


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
        list_serializer_class = ManagerCashierListSerializer
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
