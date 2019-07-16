from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.db.models import Count
from user.models import Manager

class SellerPagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        user = self.request.user
        manager_list = []
        
        if user.is_authenticated and user.user_type == 4:
            manager_list = [{'id':user.pk,'username':user.username} for user in Manager.objects.filter(my_store=self.request.user.my_store, is_active=True)]
        
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,            
            'manager_list': manager_list,            
            'results': data
        })
