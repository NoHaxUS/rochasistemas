from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from utils.serializers.rule import RulesMessageSerializer
from utils.permissions import General
from utils.models import RulesMessage


class RulesMessageView(ModelViewSet):
	queryset = RulesMessage.objects.all()
	serializer_class = RulesMessageSerializer
	permission_classes = [General,]

	def list(self, request, pk=None):
		from core.models import Store
		store_id = request.GET.get('store')
		store = Store.objects.get(pk=store_id)

		rules= RulesMessage.objects.filter(store=store)
		serializer = self.get_serializer(rules, many=True)

		return Response(serializer.data)
        