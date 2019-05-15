from core.paginations import PageNumberPagination
from rest_framework.response import Response

class TicketPagination(PageNumberPagination):
    page_size = 1

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
