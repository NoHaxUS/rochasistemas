from core.paginations import PageNumberPagination
from rest_framework.response import Response
from decimal import Decimal
from user.models import CustomUser as User

class ReleasePagination(PageNumberPagination):
    page_size = 30

    def get_paginated_response(self, data):        
        entry = 0
        out = 0        
        total = 0
        users = [{"id":user.pk,"username":user.username} for user in User.objects.filter(user_type__in=[2,3], is_active=True, my_store=self.request.user.my_store)]                  
        for release in data:            
            if float(release['value']) > 0:
                entry += float(release['value'])                
            else:
                out += float(release['value'])
            total += float(release['value'])            
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,            
            'entry': entry,
            'out': out,            
            'total': total,
            'users': users,
            'results': data
        })
