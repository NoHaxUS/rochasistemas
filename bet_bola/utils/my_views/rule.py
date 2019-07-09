from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from utils.serializers.rule import RulesMessageSerializer
from core.permissions import StoreIsRequired, UserIsFromThisStore
from user.permissions import IsAdmin
from utils.models import RulesMessage
from filters.mixins import FiltersMixin


class RulesMessageView(FiltersMixin, ModelViewSet):
	queryset = RulesMessage.objects.all()
	serializer_class = RulesMessageSerializer
	permission_classes = [IsAdmin]

	filter_mappings = {
		'store': 'store'
	}
	
	def perform_create(self, serializer):		
		store = self.request.user.my_store
		text = serializer.validated_data['text']
		rules = RulesMessage.objects.filter(store=store).first()	
		if rules:
			rules.text = text
			rules.save()
			return {
				'success': True,
				'message': 'Regra criada com sucesso'
			}
		
		RulesMessage.objects.create(store=store, text=text)

		return {
			'success': True,
			'message': 'Regra criada com sucesso'
		}
        