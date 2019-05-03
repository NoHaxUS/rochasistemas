
class MarketView(ModelViewSet):
    queryset = Market.objects.exclude(cotations__market__name='1X2').distinct()
    serializer_class = MarketSerializer    
    permission_classes = [General, GamePermission]
    
    def list(self, request, pk=None):
        queryset = Market.objects.all()

        game_id = request.GET.get('game_id')
        my_cotations_qs = Cotation.objects.filter(game=game_id).exclude(market__name='1X2')
        queryset = queryset.prefetch_related(Prefetch('cotations', queryset=my_cotations_qs, to_attr='my_cotations'))
        queryset = queryset.annotate(cotations_count=Count('cotations', filter=Q(cotations__game__pk=game_id))).filter(cotations_count__gt=0).exclude(name='1X2')


        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
              
        serializer = self.get_serializer(page, many=True)
        return Response(serializer.data)


