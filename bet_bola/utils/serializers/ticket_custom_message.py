from rest_framework import serializers
from core.models import Store
from utils.models import TicketCustomMessage

class TicketCustomMessageSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model =  TicketCustomMessage
		fields = ('text',)

