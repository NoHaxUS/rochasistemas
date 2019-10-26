from rest_framework import permissions
from core.exceptions import NotAllowedException

class BaseHistoryPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_anonymous and \
            request.user.user_type in [2,3,4]:            
            return 	True
        raise NotAllowedException(detail="Você não tem permissão para realizar essa operação.")

class SellerCashierPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_anonymous and \
			request.user.user_type in [2,3,4]:			
            return 	True
        raise NotAllowedException(detail="Você não tem permissão para visualizar.")    


class CashierCloseSellerPermission(permissions.BasePermission):
    
    def has_permission(self, request, view):     
        if request.method not in permissions.SAFE_METHODS and request.user.user_type == 3 and not request.user.manager.can_close_cashier:            
            raise NotAllowedException(detail="Você não tem permissão para fechar o caixa.")
        if not request.user.is_anonymous and \
			request.user.user_type in [3,4]:
            return 	True

        raise NotAllowedException(detail="Você não tem permissão para realizar essa operação.")    
    
    def has_object_permission(self, request, view, obj):        
        if request.user.user_type in [3,4]:
            if request.user.user_type == 3 and request.user.manager.manager_assoc.filter(pk=obj.pk) and request.user.manager.can_close_cashier:
                return True
            if request.user.user_type == 4 and request.user.my_store == obj.my_store:
                return True
        raise NotAllowedException(detail="Você não tem permissão para realizar essa operação.")


class ManagerCashierPermission(permissions.BasePermission):
    
    def has_permission(self, request, view):
        if not request.user.is_anonymous and \
			request.user.user_type in [3,4]:			            
            return 	True
        raise NotAllowedException(detail="Você não tem permissão para visualizar.")    


class CashierCloseManagerPermission(permissions.BasePermission):
    
    def has_permission(self, request, view):
        if not request.user.is_anonymous and \
			request.user.user_type == 4:            
            return True
        raise NotAllowedException(detail="Você não tem permissão para realizar essa operação.")    
    
    def has_object_permission(self, request, view, obj):
        if request.user.user_type == 4 and request.user.my_store == obj.my_store:            
            return True
        raise NotAllowedException(detail="Você não tem permissão para realizar essa operação.")    
