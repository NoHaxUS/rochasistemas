from rest_framework import serializers
from core.models import Store
from utils.models import TicketCustomMessage

class TicketCustomMessageSerializer(serializers.HyperlinkedModelSerializer):

	store = serializers.SlugRelatedField(read_only=True,slug_field='id')

	class Meta:
		model =  TicketCustomMessage
		fields = ('text','store')

