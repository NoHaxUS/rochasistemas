from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from utils.serializers.rule import RulesMessageSerializer
from core.permissions import StoreIsRequired, UserIsFromThisStore
from utils.models import RulesMessage


class RulesMessageView(ModelViewSet):
	queryset = RulesMessage.objects.all()
	serializer_class = RulesMessageSerializer
	permission_classes = [StoreIsRequired, UserIsFromThisStore,]

	def list(self, request, pk=None):
		from core.models import Store
		store_id = request.GET.get('store')
		store = Store.objects.get(pk=store_id)

		rules= RulesMessage.objects.filter(store=store)
		serializer = self.get_serializer(rules, many=True)

		return Response(serializer.data)
	
	def perform_create(self, serializer):		
		store = self.request.user.my_store
		text = serializer.validated_data['text']		
		if RulesMessage.objects.filter(store=store).exists():
			rule = RulesMessage.objects.get(store=store)
			rule.text = text
			rule.save()
			return rule
		return RulesMessage.objects.create(store=store, text=text)
        