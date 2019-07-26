from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from user.serializers.manager import ManagerSerializer
from user.serializers.seller import SellerSerializer
from user.serializers.punter import PunterSerializer


"""
class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):        
        serializer = self.serializer_class(data=request.data, context={'request': request})

        serializer.is_valid(raise_exception=True)        
        user = serializer.validated_data['user']
        print(user)
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
        	user = PunterSerializer(user.punter, many=False).data
        	user_type = "punter"
        elif user.has_perm('user.be_manager'):
        	user = ManagerSerializer(user.manager,many=False).data
        	user_type = "manager"
        elif user.has_perm('user.be_seller'):
        	user = SellerSerializer(user.seller,many=False).data
        	user_type = "seller"
        elif user.has_perm('user.be_admin'):
        	user = SellerSerializer(user.admin,many=False).data
        	user_type = "admin"        
    
        return Response({
            'token': token.key,
            'user': user,
            'type': user_type            
        })
"""