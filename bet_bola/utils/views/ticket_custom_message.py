from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from user.permissions import IsAdmin
from utils.serializers.ticket_custom_message import TicketCustomMessageSerializer
from core.permissions import StoreIsRequired, UserIsFromThisStore
from utils.models import TicketCustomMessage
import json


class TicketCustomMessageView(ModelViewSet):
    queryset = TicketCustomMessage.objects.all()
    serializer_class = TicketCustomMessageSerializer
    permission_classes = [IsAdmin,]
    cache_group = 'ticket_custom_adm'
    caching_time = 60

    def list(self, request, pk=None):
        if request.user.is_authenticated:
            store_id = request.user.my_store.pk			
            ticket_custom_message= TicketCustomMessage.objects.filter(store__pk=store_id)
            serializer = self.get_serializer(ticket_custom_message, many=True)

            return Response(serializer.data)
        return Response({})
    
    def create(self, validated_data):
        data = self.request.data.get('data')        
        data = json.loads(data)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)		
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer):		
        store = self.request.user.my_store
        text = serializer.validated_data['text']		
        if TicketCustomMessage.objects.filter(store=store).exists():
            ticket_custom_message = TicketCustomMessage.objects.get(store=store)
            ticket_custom_message.text = text
            ticket_custom_message.save()
            return ticket_custom_message
        return TicketCustomMessage.objects.create(store=store, text=text)
