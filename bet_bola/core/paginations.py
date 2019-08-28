from django.core.paginator import Paginator
from django.utils.functional import cached_property
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from math import ceil
import inspect


class MyPaginator(Paginator):    

    def page(self, number):
        """Return a Page object for the given 1-based page number."""
        number = self.validate_number(number)
        
        count = 0
        bottom = None
        top = None
        games_bottom = (number - 1) * self.per_page
        games_top = games_bottom + self.per_page

        for l in range(len(self.object_list)):                        
            if (games_bottom <= count and bottom is None) or (games_bottom == 0 and bottom is None):                
                bottom = l
                games_bottom = count
            if count >= games_top:
                top = l         
                break
            count+= self.object_list[l].games.__len__()
                
        if top is None:                        
            return self._get_page(self.object_list[bottom:], number, self)
        return self._get_page(self.object_list[bottom:top], number, self)
    
    @cached_property
    def count(self):
        """Return the total number of objects, across all pages."""
        c = getattr(self.object_list, 'count', None)
        if callable(c) and not inspect.isbuiltin(c) and method_has_no_args(c):
            return c()
        count = 0
        for l in self.object_list:            
            count += l.games.__len__()        
        return count

    @cached_property
    def num_pages(self):
        """Return the total number of pages."""
        if self.count == 0 and not self.allow_empty_first_page:
            return 0        
        hits = max(1, self.count - self.orphans)
        
        if self.count - self.object_list[len(self.object_list) - 1].games.__len__() < self.per_page:
            return ceil(hits / self.per_page)  - 1
        return ceil(hits / self.per_page)  
        

class GameListPagination(PageNumberPagination):
    django_paginator_class = MyPaginator
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


class GameTablePagination(PageNumberPagination):
    page_size = 200

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

class StandardSetPagination(PageNumberPagination):
    page_size = 25

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



class CotationsListSetPagination(PageNumberPagination):
    page_size = 25

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


