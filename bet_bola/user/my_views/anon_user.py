from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from user.models import AnonymousUser
from user.permissions import IsSeller, StoreGiven
from user.serializers.anonymous import AnonymousUserSerializer

class AnonymousUserView(ModelViewSet):
    queryset = AnonymousUser.objects.all()
    serializer_class = AnonymousUserSerializer    

    def list(self, request, pk=None):
        store_id = request.GET['store'] 

        queryset = self.queryset.filter(my_store__id=store_id)
        
        page = self.paginate_queryset(queryset)        

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)    
