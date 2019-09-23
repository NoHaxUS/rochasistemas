from django.core.paginator import Paginator
from django.utils.functional import cached_property
from django.db.models import Q, Count
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.db.models import Count
from user.models import CustomUser, Seller, Manager
from ticket.models import Ticket,Payment
from decimal import Decimal
from math import ceil


class TicketCancelationPagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):    
        paid_by_list = [{'id':user.pk,'username':user.username} for user in CustomUser.objects.filter(my_canceled_tickets_who_i_paid__isnull=False, my_store=self.request.user.my_store).distinct()]
        cancelled_by_list = [{'id':user.pk,'username':user.username} for user in CustomUser.objects.filter(my_canceled_tickets__isnull=False, my_store=self.request.user.my_store).distinct()]
   
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,            
            'paid_by_list': paid_by_list,
            'cancelled_by_list': cancelled_by_list,
            'results': data
        })


class TicketValidationPagination(PageNumberPagination):
    page_size = 10   

    def get_paginated_response(self, data):
        paid_by_list = [{'id':user.pk,'username':user.username} for user in CustomUser.objects.filter(my_ticket_validations__isnull=False, my_store=self.request.user.my_store).distinct()]
        
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,            
            'paid_by_list': paid_by_list,            
            'results': data
        })


class SellerCashierHistoryPagination(PageNumberPagination):
    page_size = 10    

    def get_paginated_response(self, data):        
        register_by_list = [{'id':user.pk,'username':user.username} for user in CustomUser.objects.filter(sellercashierhistory__isnull=False, my_store=self.request.user.my_store).distinct()]        
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,            
            'register_by_list': register_by_list,              
            'results': data
        })


class ManagerCashierHistoryPagination(PageNumberPagination):
    page_size = 10    

    def get_paginated_response(self, data):        
        register_by_list = [{'id':user.pk,'username':user.username} for user in CustomUser.objects.filter(sellercashierhistory__isnull=False, my_store=self.request.user.my_store).distinct()]        

        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,            
            'register_by_list': register_by_list,              
            'results': data
        })


class CreditTransactionsPagination(PageNumberPagination):
    page_size = 10    

    def get_paginated_response(self, data):  
        creditor_list = [{'id':user.pk,'username':user.username} for user in CustomUser.objects.filter(pk=self.request.user.pk).distinct()]
        if self.request.user.user_type == 3:
            seller_list = [{'id':user.pk,'username':user.username} for user in CustomUser.objects.filter(credit_transactions__isnull=False, seller__my_manager__pk=self.request.user.pk, my_store=self.request.user.my_store).distinct()]
        else:
            seller_list = [{'id':user.pk,'username':user.username} for user in CustomUser.objects.filter(credit_transactions__isnull=False, my_store=self.request.user.my_store).distinct()]
            
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,                                    
            'results': data,
            'creditor_list':creditor_list,
            'seller_list':seller_list
        })


class SellersCashierPagination(PageNumberPagination):
    page_size = 30

    def get_paginated_response(self, data):                
        if self.request.user.user_type == 4:        
            sellers = [{'id':seller.pk,'username':seller.username} for seller in Seller.objects.filter(payment__status=2, my_store=self.request.user.my_store).distinct()]
        elif self.request.user.user_type == 3:            
            sellers = [{'id':user.pk,'username':user.username} for user in self.request.user.manager.manager_assoc.filter(payment__status=2, my_store=self.request.user.my_store).distinct()]
        else:
            sellers = [{'id':user.pk,'username':user.username} for user in Seller.objects.none()]        

        data = data.pop()
        entry = float(data["entry"])                
        out = float(data["out"])
        won_bonus = float(data["won_bonus"])
        comissions_sum = float(data["comission"])
        total_out = float(data["total_out"])
        profit = float(data["profit"])
        

        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,            
            'sellers':sellers,
            'entry': entry,
            'out': out,
            'won_bonus': won_bonus,
            'comissions_sum': comissions_sum,
            'total_out': total_out,
            'profit': profit,
            'results': data['data']
        })


class ManagersCashierPagination(PageNumberPagination):
    page_size = 30

    def get_paginated_response(self, data):        
        managers = [{"id":manager.pk,"username":manager.username} for manager in Manager.objects.filter(manager_assoc__payment__status=2, my_store=self.request.user.my_store).distinct()]
        data = data.pop()
        entry = float(data["entry"])                
        out = float(data["out"])
        won_bonus = float(data["won_bonus"])
        comissions_sum = float(data["comission"])
        seller_comissions_sum = float(data["seller_comission"])
        total_out = float(data["total_out"])
        profit = float(data["profit"])
                

        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,            
            'entry': entry,
            'out': out,
            'won_bonus': won_bonus,
            'comissions_sum': comissions_sum,
            'seller_comissions_sum': seller_comissions_sum,
            'total_out': total_out,
            'managers': managers,
            'profit':profit,
            'results': data['data']
        })

class SellerCashierPaginator(Paginator):  
    
    @cached_property
    def count(self):
        """Return the total number of objects, across all pages."""
        count = 0
        tickets = Ticket.objects.filter(Q(payment__status=2, payment__who_paid__pk=self.object_list.first().pk) &
        (Q(closed_in_for_seller=False) | Q(closed_out_for_seller=False, status__in=[4,2]))).exclude(Q(status__in=[5,6]) | Q(available=False))
        
        if tickets:  
            count = tickets.count()
        return count    


class SellerCashierPagination(PageNumberPagination):
    django_paginator_class = SellerCashierPaginator
    page_size = 30

    def get_paginated_response(self, data):                
        if self.request.user.user_type == 4:        
            sellers = [{'id':seller.pk,'username':seller.username} for seller in Seller.objects.filter(payment__status=2, my_store=self.request.user.my_store).distinct()]
        elif self.request.user.user_type == 3:            
            sellers = [{'id':user.pk,'username':user.username} for user in self.request.user.manager.manager_assoc.filter(payment__status=2, my_store=self.request.user.my_store).distinct()]
        else:
            sellers = [{'id':user.pk,'username':user.username} for user in Seller.objects.none()]
        
        tickets = data[0]['tickets']
        
        page = int(self.request.GET.get('page',1)) 

        if page == 1:
            tickets = tickets[0:self.page_size]
        tickets = tickets[self.page_size * (page - 1) : (page * self.page_size)]
        
        data[0]['tickets'] = tickets

        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,                        
            'sellers': sellers,
            'results': data
        })


class ManagerCashierPaginator(Paginator):  
    
    @cached_property
    def count(self):
        """Return the total number of objects, across all pages."""
        count = 0
        tickets = Ticket.objects.filter(Q(payment__status=2, payment__who_paid__seller__my_manager__pk=self.object_list.first().pk) &
            (Q(closed_in_for_manager=False) | Q(closed_out_for_manager=False, status__in=[4,2])))\
            .exclude(Q(status__in=[5,6]) | Q(available=False))
        
        if tickets:  
            count = tickets.count()
        return count    

class ManagerCashierPagination(PageNumberPagination):
    django_paginator_class = ManagerCashierPaginator
    page_size = 30

    def get_paginated_response(self, data):                
        managers = [{"id":manager.pk,"username":manager.username} for manager in Manager.objects.filter(manager_assoc__payment__status=2, my_store=self.request.user.my_store).distinct()]                                   
        
        tickets = data[0]['tickets']
        
        page = int(self.request.GET.get('page',1)) 

        if page == 1:
            tickets = tickets[0:self.page_size]
        tickets = tickets[self.page_size * (page - 1) : (page * self.page_size)]
        
        data[0]['tickets'] = tickets

        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,                        
            'managers': managers,            
            'results': data
        })


class ManagerSpecificCashierPagination(PageNumberPagination):
    page_size = 30

    def get_paginated_response(self, data):        
        entry = 0
        out = 0
        comissions_sum = 0
        won_bonus_sum = 0
        total_out = 0
        seller_comissions_sum = 0
        users = []                   
        for user in data:
            users.append({"id":user["id"],"username":user["username"]})            
            entry += float(user["entry"])                
            out += float(user["out"])
            won_bonus_sum += float(user["won_bonus"])
            comissions_sum += float(user["comission"])
            seller_comissions_sum += float(user["comission_seller"])            
            total_out += float(user["total_out"])
        
        if self.request.user.manager.comission_based_on_profit:
            comissions_sum = Decimal(entry - total_out) * self.request.user.manager.comissions.profit_comission / 100
        
        if comissions_sum < 0:
            comissions_sum = 0

        page = int(self.request.GET.get('page',1))         
        if page == 1:
            data = data[0:self.page_size]
        data = data[self.page_size * (page - 1) : (page * self.page_size)]
        
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,            
            'entry': entry,
            'out': out,
            'won_bonus_sum': won_bonus_sum,
            'comissions_sum': comissions_sum,
            'seller_comissions_sum': seller_comissions_sum,
            'total_out': total_out,
            'users': users,
            'is_comission_based_on_profit':self.request.user.manager.comission_based_on_profit,
            'results': data
        })
        