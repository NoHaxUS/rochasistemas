
class SellerView(ModelViewSet):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer   
    permission_classes = [SellerViewPermission,] 

    def list(self, request, pk=None):
        store_id = request.GET.get('store')

        queryset = self.queryset.filter(my_store__id=store_id)

        page = self.paginate_queryset(queryset)        

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)    

    def destroy(self, request, *args, **kwargs):
        seller = self.get_object()
        
        self.perform_destroy(seller)        
        return Response(status=status.HTTP_204_NO_CONTENT)
                

    @action(methods=['get'], detail=True)
    def pay_seller(self, request, pk=None):
        seller = self.get_object()
        who_reseted_revenue = str(request.user.pk) + ' - ' + request.user.username
        seller.reset_revenue(who_reseted_revenue)

        return Response({'success':'Cambista Pago'})

    @action(methods=['post'], detail=True)
    def add_credit(self, request, pk=None):
        try:
            valor = request.data['value']
        except KeyError:
            return Response({"Error": "Entrada invalida. Dica:{'value':'?'}"})

        instance = self.get_object()        
        if request.user.has_perm('user.be_manager'):            
            if request.user.manager.my_store.pk != instance.my_store.pk:
                return Response({'failed':'Gerente não pertence a mesma loja que o vendedor em questão'})
            instance.credit_limit += valor
            credit_transation = request.user.manager.manage_credit(instance)
            return Response(credit_transation)

