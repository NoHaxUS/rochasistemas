from rest_framework import serializers
from user.serializers.seller import SellerSerializer
from ticket.models import Payment

class PaymentSerializer(serializers.HyperlinkedModelSerializer):

	who_set_payment = SellerSerializer(read_only=True)
	status = serializers.SerializerMethodField()
	
	class Meta:
		model = Payment
		fields =  ('who_set_payment','status','date')

	def get_status(self, obj):
		return obj.get_status_display()




class PaymentSerializerWithSeller(serializers.HyperlinkedModelSerializer):

	who_set_payment = serializers.SlugRelatedField(slug_field="first_name", read_only=True)
	status = serializers.SerializerMethodField()
	date = serializers.DateTimeField(format='%d/%m/%Y %H:%M')
	
	class Meta:
		model = Payment
		fields =  ('who_set_payment','status','date')

	def get_status(self, obj):
		return obj.get_status_display()