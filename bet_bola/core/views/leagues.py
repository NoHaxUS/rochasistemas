class LeagueView(ModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer
    permission_classes = [General,]

