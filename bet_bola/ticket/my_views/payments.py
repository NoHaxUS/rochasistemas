from rest_framework.viewsets import ModelViewSet
from ticket.serializers.payment import PaymentSerializer
from ticket.models import Payment

class PaymentView(ModelViewSet):
	queryset = Payment.objects.all()
	serializer_class = PaymentSerializer