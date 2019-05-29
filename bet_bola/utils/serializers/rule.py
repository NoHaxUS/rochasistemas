from rest_framework import serializers
from core.models import Store
from utils.models import RulesMessage

class RulesMessageSerializer(serializers.HyperlinkedModelSerializer):

	store = serializers.SlugRelatedField(read_only=True,slug_field='id')

	class Meta:
		model =  RulesMessage
		fields = ('text','store')

