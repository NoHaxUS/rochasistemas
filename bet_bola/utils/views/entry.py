from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from filters.mixins import FiltersMixin
from user.models import CustomUser
from user.permissions import IsAdmin
from utils.paginations import EntryPagination
from utils.models import Entry
from utils.serializers.entry import EntrySerializer
from utils.permissions import EntryPermission
import json, datetime

class EntryView(FiltersMixin, ModelViewSet):
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer
    pagination_class = EntryPagination
    permission_classes = [EntryPermission, ]


    filter_mappings = {
        'user':'user__pk',
        'start_creation_date': 'creation_date__date__gte',
        'end_creation_date': 'creation_date__date__lte',
    }

    filter_value_transformations = {
        'start_creation_date': lambda val: datetime.datetime.strptime(val, '%d/%m/%Y').strftime('%Y-%m-%d'),
        'end_creation_date': lambda val: datetime.datetime.strptime(val, '%d/%m/%Y').strftime('%Y-%m-%d'),        
    }

    def list(self, request, pk=None):        
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(queryset, many=True)            
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


    def get_queryset(self):
        user = self.request.user
        if user.user_type == 2:
            return Entry.objects.filter(user=user).exclude(closed=True).order_by('-creation_date')
        elif user.user_type == 3:
            return Entry.objects.filter(Q(user=user.pk) | Q(user__in=user.manager.manager_assoc.all())).exclude(closed=True).order_by('-creation_date')
        return Entry.objects.filter(store=user.my_store).order_by('-creation_date')
        
    def create(self, request, *args, **kwargs):        
        data = request.data.get('data')
        data = json.loads(data)
        if request.user.user_type == 2:
            data = {"user":request.user.pk, "value":data.get("value"), "description":data.get("description"), "store":request.user.my_store.pk}         
        else:    
            data = {"user":int(data.get("user")), "value":data.get("value"), "description":data.get("description"), "store":request.user.my_store.pk}         
        serializer = self.get_serializer(data=data)        
        serializer.is_valid(raise_exception=True)        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)                        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['get'], detail=True, permission_classes=[IsAdmin])
    def close_entry(self, request, pk=None):
        entry = self.get_object()
        entry.closed = True
        entry.save()
        return Response({'success':True, 'message': 'Lançamento fechado.'})