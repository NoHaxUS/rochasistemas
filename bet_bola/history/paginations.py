from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.db.models import Count
from user.models import CustomUser, Seller
from ticket.models import Ticket

class CancelationHistoryPagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):    
        paid_by_list = [{'id':user.pk,'username':user.username} for user in CustomUser.objects.filter(my_canceled_tickets_who_i_paid__isnull=False).distinct()]
        cancelled_by_list = [{'id':user.pk,'username':user.username} for user in CustomUser.objects.filter(my_canceled_tickets__isnull=False).distinct()]
   
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


class TicketValidationHistoryPagination(PageNumberPagination):
    page_size = 10   

    def get_paginated_response(self, data):
        paid_by_list = [{'id':user.pk,'username':user.username} for user in CustomUser.objects.filter(my_ticket_validations__isnull=False).distinct()]
        
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


class RevenueHistorySellerPagination(PageNumberPagination):
    page_size = 10
    register_by_list = [{'id':user.pk,'username':user.username} for user in CustomUser.objects.filter(revenuehistoryseller__isnull=False).distinct()]        

    def get_paginated_response(self, data):        
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,            
            'register_by_list': self.register_by_list,              
            'results': data
        })


class RevenueHistoryManagerPagination(PageNumberPagination):
    page_size = 10
    register_by_list = [{'id':user.pk,'username':user.username} for user in CustomUser.objects.filter(revenuehistorymanager__isnull=False).distinct()]        

    def get_paginated_response(self, data):        
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,            
            'register_by_list': self.register_by_list,              
            'results': data
        })


class ManagerTransactionsHistoryPagination(PageNumberPagination):
    page_size = 10    

    def get_paginated_response(self, data):  
        creditor_list = [{'id':user.pk,'username':user.username} for user in CustomUser.objects.filter(pk=self.request.user.pk).distinct()]
        if self.request.user.user_type == 3:
            seller_list = [{'id':user.pk,'username':user.username} for user in Seller.objects.filter(managertransactions__isnull=False, my_manager__pk=self.request.user.pk).distinct()]
        else:
            seller_list = [{'id':user.pk,'username':user.username} for user in Seller.objects.filter(managertransactions__isnull=False).distinct()]
            
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