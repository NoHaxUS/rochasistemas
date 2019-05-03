
class ManagerView(ModelViewSet):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer
    permission_classes = [ManagerViewPermission,]

    def list(self, request, pk=None):
        store_id = request.GET['store']        

        queryset = self.queryset.filter(my_store__id=store_id)
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)   
                
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def pay_manager(self, request, pk=None):
        manager = self.get_object()
        who_reseted_revenue = str(request.user.pk) + ' - ' + request.user.username        
        manager.reset_revenue(who_reseted_revenue)
        
        messages.success(request, 'Gerentes Pagos')
