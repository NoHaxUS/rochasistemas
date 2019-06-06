from core.paginations import PageNumberPagination
from rest_framework.response import Response
from ticket.models import Payment
from user.models import Seller, Manager
from decimal import Decimal

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
        seller_comission_sum = 0
        managers = [manager.username for manager in Manager.objects.filter(manager_assoc__payment__status=2).distinct()]                                   
        incomes = {}
        outs = {}
        for ticket in data:
            entry += float(ticket["bet_value"])                        
            
            if ticket["manager"]:                
                if not incomes.get(ticket["manager"]["username"], None):
                    incomes[ticket["manager"]["username"]] = {}
                    outs[ticket["manager"]["username"]] = {}

                if not incomes[ticket["manager"]["username"]].get(ticket["bet_type"], None): 
                    incomes[ticket["manager"]["username"]][ticket["bet_type"]] = 0
                    outs[ticket["manager"]["username"]][ticket["bet_type"]] = 0
                
                incomes[ticket["manager"]["username"]][ticket["bet_type"]] += Decimal(ticket["bet_value"])
                if ticket["status"] == "Venceu":
                    outs[ticket["manager"]["username"]][ticket["bet_type"]] += Decimal(ticket["reward"]["value"])
            
            if ticket["status"] == 'Venceu':
                out += float(ticket["reward"]["value"])            
            seller_comission_sum += float(ticket["comission"])

        manager_comission_sum = 0
        for manager in incomes:
            manager_obj = Manager.objects.get(username=manager)            
            comissions = {"simple":manager_obj.comissions.simple,
                            "double":manager_obj.comissions.double,
                            "triple":manager_obj.comissions.triple,
                            "fourth":manager_obj.comissions.fourth,
                            "fifth":manager_obj.comissions.fifth,
                            "sixth":manager_obj.comissions.sixth}

            manager_comission = 0
            for comission_type in incomes[manager]:                                
                if manager_obj.comission_based_on_profit:                    
                    manager_comission += (incomes[manager][comission_type] - outs[manager][comission_type]) * manager_obj.comissions.profit_comission / 100
                else:
                    manager_comission += incomes[manager][comission_type] * comissions.get(comission_type, manager_obj.comissions.sixth_more) / 100
            
            if manager_comission <= 0:
                manager_comission = 0

            manager_comission_sum += manager_comission
        
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
            'manager_comission': manager_comission_sum,
            'seller_comission': seller_comission_sum,
            'results': data
        })