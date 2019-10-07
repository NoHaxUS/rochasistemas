from core.paginations import PageNumberPagination
from rest_framework.response import Response
from ticket.models import Payment
from user.models import Seller, Manager
from decimal import Decimal

class TicketPagination(PageNumberPagination):
    page_size = 30

    def get_paginated_response(self, data):
        show_buttons = True
        if self.request.user.user_type == 2:
            show_buttons = False
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'show_buttons':show_buttons,            
            'results': data
        })

