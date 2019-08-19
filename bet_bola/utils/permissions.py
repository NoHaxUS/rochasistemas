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
        raise NotAllowedException(detail="Você não tem permissão para essa operação.")    


class RulePermission(permissions.BasePermission):
    def has_permission(self, request, view):        
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            if request.user.user_type == 4:
                return True
                
        raise NotAllowedException(detail="Você não tem permissão para visualizar.")

    def has_object_permission(self, request, view, obj):         
        if not request.user.is_anonymous:
            if request.user.user_type == 4:
                return True            
        raise NotAllowedException(detail="Você não tem permissão para essa operação.")    
    
    
