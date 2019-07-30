from rest_framework import permissions
from core.exceptions import NotAllowedException

class EntryPermission(permissions.BasePermission):
    def has_permission(self, request, view):        
        if not request.user.is_anonymous and \
			request.user.user_type in [2,3,4]:			            
            return 	True
        raise NotAllowedException(detail="Você não tem permissão para visualizar.")

    def has_object_permission(self, request, view, obj):         
        if not request.user.is_anonymous:
            if request.user.user_type == 4:
                return True
            elif obj.user == request.user:
                return True				
            elif request.user.user_type == 3 and request.user.manager.manager_assoc.filter(pk=obj.user.pk).exists():
                return True

        raise NotAllowedException(detail="Você não tem permissão para essa operação.")    
    
    
