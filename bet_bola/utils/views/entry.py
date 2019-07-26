from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from filters.mixins import FiltersMixin
from user.models import CustomUser
from utils.paginations import EntryPagination
from utils.models import Entry
from utils.serializers.entry import EntrySerializer
from utils.permissions import EntryPermission
import json

class EntryView(FiltersMixin, ModelViewSet):
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer
    pagination_class = EntryPagination
    permission_classes = [EntryPermission, ]

    filter_mappings = {
        'user':'user__pk',
        'start_creation_date': 'creation_date__gte',
        'end_creation_date': 'creation_date__lte',
    }

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 2:
            return Entry.objects.filter(user=user).order_by('-creation_date')
        elif user.user_type == 3:
            return Entry.objects.filter(Q(user=user.pk) | Q(user__in=user.manager.manager_assoc.all())).order_by('-creation_date')
        return Entry.objects.filter(store=user.my_store).order_by('-creation_date')
        
    def create(self, request, *args, **kwargs):        
        data = request.data.get('data')
        data = json.loads(data)
        if request.user.user_type == 2:
            data = {"user":request.user.pk, "value":data.get("value"), "store":request.user.my_store.pk}         
        else:    
            data = {"user":int(data.get("user")), "value":data.get("value"), "store":request.user.my_store.pk}         
        serializer = self.get_serializer(data=data)        
        serializer.is_valid(raise_exception=True)        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)                        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)