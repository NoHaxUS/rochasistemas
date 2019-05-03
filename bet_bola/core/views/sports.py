class SportView(ModelViewSet):
    queryset = Sport.objects.all()
    serializer_class = SportSerializer
    permission_classes = [General,]

