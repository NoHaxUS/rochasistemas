from rest_framework import permissions
from core.exceptions import NotAllowedException

class ReleasePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_anonymous and \
			request.user.user_type in [2,3,4]:			
            return 	True
        raise NotAllowedException(detail="Você não tem permissão para visualizar.")

    def has_object_permission(self, request, view, obj):        
        if request.user.is_anonymous:
            if request.user.user_type == 4:
                return True
            if obj.my_manager and request.user.pk == obj.my_manager.pk:
                return True				
        raise NotAllowedException(detail="Você não tem permissão para essa operação.")    
    
    
