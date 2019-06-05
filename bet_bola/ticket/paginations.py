from core.paginations import PageNumberPagination
from rest_framework.response import Response
from ticket.models import Payment
from user.models import Seller, Manager

class TicketPagination(PageNumberPagination):
    page_size = 30

    def get_paginated_response(self, data):        
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,            
            'results': data
        })


class RevenueSellerPagination(PageNumberPagination):
    page_size = 30

    def get_paginated_response(self, data):        
        entry = 0
        out = 0
        comissions_sum = 0
        sellers = [seller.username for seller in Seller.objects.filter(payment__status=2).distinct()]                   
        for ticket in data:
            entry += float(ticket["bet_value"])
            if ticket["status"] == 'Venceu':
                out += float(ticket["reward"]["value"])            
            out += float(ticket["comission"])
            comissions_sum += float(ticket["comission"])
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,            
            'entry': entry,
            'out': out,
            'comissions_sum': comissions_sum,
            'sellers': sellers,
            'results': data
        })

    
class RevenueManagerPagination(PageNumberPagination):
    page_size = 30

    def get_paginated_response(self, data):        
        entry = 0
        out = 0
        managers = [manager.username for manager in Manager.objects.filter(manager_assoc__payment__status=2).distinct()]                                   
        
        for ticket in data:
            entry += float(ticket["bet_value"])                        
            
            if ticket["manager"]:                
                if ticket["manager"]["comission_based_on_profit"]:
                    pass                   
                else:
                    pass

            if ticket["status"] == 'Venceu':
                out += float(ticket["reward"]["value"])            
            out += float(ticket["comission"])
        
            
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,            
            'entry': entry,
            'out': out,            
            'managers': managers,
            'results': data
        })