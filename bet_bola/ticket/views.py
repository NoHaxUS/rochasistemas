from rest_framework.viewsets import ModelViewSet, ViewSet
from .models import *
from .serializers import *


class TicketView(ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer


class RewardView(ModelViewSet):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer


class PaymentView(ModelViewSet):
	queryset = Payment.objects.all()
	serializer_class = PaymentSerializer