class PaymentView(ModelViewSet):
	queryset = Payment.objects.all()
	serializer_class = PaymentSerializer