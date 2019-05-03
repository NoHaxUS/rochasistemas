
class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user_type = ""

        if user.is_superuser:
        	user_type = "superuser"
        	user = {
	        	"pk":user.pk,
	        	"name":user.first_name,
	        	"username":user.username,        	
	        	"type":user_type
        	}        	
        elif user.has_perm('user.be_punter'):
        	user = PunterSerializer(user.punter, many=False)
        	user_type = "punter"
        elif user.has_perm('user.be_manager'):
        	user = ManagerSerializer(user.manager,many=False)
        	user_type = "manager"
        elif user.has_perm('user.be_seller'):
        	user = SellerSerializer(user.seller,many=False)        	
        	user_type = "seller"
        elif user.has_perm('user.be_admin'):
        	user = SellerSerializer(user.admin,many=False)
        	user_type = "admin"        
        
        return Response({
            'token': token.key,
            'user': user.data,
            'type': user_type            
        })
