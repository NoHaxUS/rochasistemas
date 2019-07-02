from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.db.models import Count
from user.models import CustomUser
from ticket.models import Ticket

class CancelationHistoryPagination(PageNumberPagination):
    page_size = 10
    paid_by_list = [{'id':user.pk,'username':user.username} for user in CustomUser.objects.filter(my_canceled_tickets_who_i_paid__isnull=False).distinct()]
    cancelled_by_list = [{'id':user.pk,'username':user.username} for user in CustomUser.objects.filter(my_canceled_tickets__isnull=False).distinct()]
    ticket_id_list = [{'id':ticket.ticket_id} for ticket in Ticket.objects.filter(ticketcancelationhistory__isnull=False).distinct()]

    def get_paginated_response(self, data):        
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,            
            'paid_by_list': self.paid_by_list,
            'cancelled_by_list': self.cancelled_by_list,
            'ticket_id_list': self.ticket_id_list,
            'results': data
        })


class TicketValidationHistoryPagination(PageNumberPagination):
    page_size = 10
    paid_by_list = [{'id':user.pk,'username':user.username} for user in CustomUser.objects.filter(my_ticket_validations__isnull=False).distinct()]    


    def get_paginated_response(self, data):        
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,            
            'paid_by_list': self.paid_by_list,            
            'results': data
        })
