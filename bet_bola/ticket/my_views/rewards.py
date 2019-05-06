from rest_framework.viewsets import ModelViewSet
from ticket.serializers.reward import RewardSerializer
from ticket.models import Reward

class RewardView(ModelViewSet):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer
    