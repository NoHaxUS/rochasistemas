class GeneralConfigurationsView(ModelViewSet):
    queryset = GeneralConfigurations.objects.all()
    serializer_class = GeneralConfigurationsSerializer    

