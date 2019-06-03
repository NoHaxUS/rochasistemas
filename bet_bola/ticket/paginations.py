from core.paginations import PageNumberPagination
from rest_framework.response import Response

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


class RevenuePagination(PageNumberPagination):
    page_size = 30

    def get_paginated_response(self, data):        
        entry = 0
        out = 0
        sellers = []
        for ticket in data:
            entry += float(ticket["bet_value"])
            if ticket["status"] == 'Venceu':
                out += float(ticket["reward"]["value"])
            sellers.append(ticket["payment"]["who_paid"])
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,            
            'entry': entry,
            'out': out,
            'sellers': sellers,
            'results': data
        })