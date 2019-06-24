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

class RevenueGeneralSellerPagination(PageNumberPagination):
    page_size = 30

    def get_paginated_response(self, data):        
        entry = 0
        out = 0
        comissions_sum = 0
        won_bonus_sum = 0
        total_out = 0
        users = []                   
        for user in data:
            users.append({"id":user["id"],"username":user["username"]})            
            entry += float(user["entry"])                
            out += float(user["out"])
            won_bonus_sum += float(user["won_bonus"])
            comissions_sum += float(user["comission"])
            total_out += float(user["total_out"])
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
            'total_out': total_out,
            'users': users,
            'results': data
        })


class RevenueGeneralManagerPagination(PageNumberPagination):
    page_size = 30

    def get_paginated_response(self, data):        
        entry = 0
        out = 0
        comissions_sum = 0
        seller_comissions_sum = 0
        won_bonus_sum = 0
        total_out = 0
        users = []                   
        for user in data:
            users.append({"id":user["id"],"username":user["username"]})            
            entry += float(user["entry"])                
            out += float(user["out"])            
            comissions_sum += float(user["comission"])
            won_bonus_sum += float(user["won_bonus"])
            seller_comissions_sum += float(user["comission_seller"])
            total_out += float(user["total_out"])
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
            'results': data
        })


class RevenueSellerPagination(PageNumberPagination):
    page_size = 30

    def get_paginated_response(self, data):        
        entry = 0
        out = 0
        comissions_sum = 0
        won_bonus_sum = 0
        sellers = [{'id':seller.pk,'username':seller.username} for seller in Seller.objects.filter(payment__status=2).distinct()]                   
        for ticket in data:
            entry += float(ticket["bet_value"])
            if ticket["status"] == 'Venceu, Ganhador Pago' or ticket["status"] == 'Venceu, Prestar Contas':
                out += float(ticket["reward"]["value"]) - float(ticket["won_bonus"])
                won_bonus_sum += float(ticket["won_bonus"])
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
            'won_bonus_sum': won_bonus_sum,
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
        managers = [{"id":manager.pk,"username":manager.username} for manager in Manager.objects.filter(manager_assoc__payment__status=2).distinct()]                                   
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
                if ticket["status"] == 'Venceu, Ganhador Pago' or ticket["status"] == 'Venceu, Prestar Contas':
                    outs[ticket["manager"]["username"]][ticket["bet_type"]] += Decimal(ticket["reward"]["value"])
            
            if ticket["status"] == 'Venceu, Ganhador Pago' or ticket["status"] == 'Venceu, Prestar Contas':
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
            'manager_comission': manager_comission_sum,
            'seller_comission': seller_comission_sum,  
            'managers': managers,            
            'results': data
        })