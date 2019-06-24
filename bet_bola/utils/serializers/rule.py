from rest_framework import serializers
from core.models import Store
from utils.models import RulesMessage

class RulesMessageSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model =  RulesMessage
		fields = ('text',)

