class RewardView(ModelViewSet):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer
    