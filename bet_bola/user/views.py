from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework import permissions, mixins, generics
from rest_framework.response import Response
from rest_framework import status
from user.models import Punter, NormalUser, CustomUser, Seller, Manager
from ticket.models import Ticket
from .serializers import PunterSerializer, NormalUserSerializer, SellerSerializer, ManagerSerializer


class PunterView(ModelViewSet):
    queryset = Punter.objects.all()
    serializer_class = PunterSerializer

    def list(self, request, pk=None):
        store_id = request.GET['store']   

        queryset = self.queryset.filter(my_store__id=store_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)     
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # def get_permissions(self):          
    #     if self.request.method in permissions.SAFE_METHODS: 
    #         return [permissions.AllowAny(),]
    #     return [permissions.IsAdminUser(),]


class NormalUserView(ModelViewSet):
    queryset = NormalUser.objects.all()
    serializer_class = NormalUserSerializer

    def list(self, request, pk=None):
        store_id = request.GET['store'] 

        queryset = self.queryset.filter(my_store__id=store_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # def get_permissions(self):    
    #     if self.request.method in permissions.SAFE_METHODS: 
    #         return [permissions.AllowAny(),]
    #     return [permissions.IsAdminUser(),]


class SellerView(ModelViewSet):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer

    def list(self, request, pk=None):
        store_id = request.GET['store']        

        queryset = self.queryset.filter(my_store__id=store_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        seller = self.get_object()

        tickets = Ticket.objects.filter(seller=seller)
        if [(ticket.reward.reward_status in ['Venceu, Pagar Apostador','Aguardando Resultados']) for ticket in tickets.all()]:
            return Response({'Error':'Cambista não pode ser deletado, pois possui bilhetes pendentes.'})

        self.perform_destroy(seller)        
        return Response(status=status.HTTP_204_NO_CONTENT)
        
        


    @action(methods=['get'], detail=True)
    def pay_seller(self, request, pk=None):
        seller = self.get_object()
        who_reseted_revenue = str(request.user.pk) + ' - ' + request.user.username
        seller.reset_revenue(who_reseted_revenue)

        return Response({'success':'Cambistas Pagos'})


    # def get_permissions(self):    
    #     if self.request.method in permissions.SAFE_METHODS: 
    #         return [permissions.AllowAny(),]
    #     return [permissions.IsAdminUser(),]


class ManagerView(ModelViewSet):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer

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
    # def get_permissions(self):        
    #     if self.request.method in permissions.SAFE_METHODS: 
    #         return [permissions.AllowAny(),]
    #     return [permissions.IsAdminUser(),]















# class PunterRegister(View):

#     def post(self, request):

#         errors = {'errors':False, 'data': []}
#         if not request.POST['full_name']:
#             errors['errors'] = True
#             errors['data'].append('O nome é obrigatório')
#         elif not request.POST['login']:
#             errors['errors'] = True
#             errors['data'].append('O login é obrigatório')
#         elif not request.POST['password']:
#             errors['errors'] = True
#             errors['data'].append('A senha é obrigatória')
#         elif not request.POST['cellphone']:
#             errors['errors'] = True
#             errors['data'].append('O Telefone é obrigatório')
#         if request.POST['login']:
#             if CustomUser.objects.filter(username=request.POST['login']).exists():
#                 errors['errors'] = True
#                 errors['data'].append('Esse login já está em uso, desculpe.')
#         if request.POST['email']:
#             if CustomUser.objects.filter(email=request.POST['email']).exists():
#                 errors['errors'] = True
#                 errors['data'].append('Esse email já está em uso, desculpe.')

#         if errors['errors']:
#             return HttpResponse(json.dumps(errors, ensure_ascii=False), content_type="application/json", status=406)
#         else:
#             punter = Punter(first_name=request.POST['full_name'],
#             email=request.POST['email'],
#             username=request.POST['login'],
#             password=request.POST['password'],
#             cellphone=request.POST['cellphone'])
#             punter.save()

#             user = authenticate(username=request.POST['login'], password=request.POST['password'])
            
#             if user is not None:
#                 login(request, user)
#                 return HttpResponse("User Created")



# class UserLogin(View):

#     def post(self, request):
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(username=username, password=password)
#         if user is not None:
#             login(request, user)
#             data = {
#                 'success':True,
#                 'message':'Logado com sucesso'
#             }
            
#             request.session['ticket'] = {}
#             request.session.modified = True

#             return UnicodeJsonResponse(data)
#         else:
#             data = {
#                 'success':False,
#                 'message':'Login ou senha inválidos'
#             }
#             return UnicodeJsonResponse(data)


# class UserLogout(View):
#     """
#     Provides users the ability to logout
#     """
    
#     def get(self, request, *args, **kwargs):
#         logout(request)
#         response = redirect('core:core_home')
#         response.delete_cookie('ticket_cookie')
#         return response

