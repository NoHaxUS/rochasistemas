from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from utils.serializers.rule import RulesMessageSerializer
from core.permissions import StoreIsRequired, UserIsFromThisStore
from user.permissions import IsAdmin
from utils.models import RulesMessage
from filters.mixins import FiltersMixin
import json


class RulesMessageView(ModelViewSet):
    queryset = RulesMessage.objects.all()
    serializer_class = RulesMessageSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        store = self.request.user.my_store
        return RulesMessage.objects.filter(store=store)

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
        rules = RulesMessage.objects.filter(store=store).first()

        RulesMessage.objects.update_or_create(
            text=rules.text,
            defaults={'text': text}
        )
