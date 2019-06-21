from rest_framework import permissions
from core.exceptions import NotAllowedException

class CancelationHistoryPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_anonymous and \
            request.user.user_type in [2,3,4]:            
            return 	True
        raise NotAllowedException(detail="Você não tem permissão para realizar essa operação.")