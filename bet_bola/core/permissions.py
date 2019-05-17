from rest_framework import permissions

class StoreIsRequired(permissions.BasePermission):
    message = "Operação não permitida. (Banca"
    def has_permission(self, request, view):
        if request.GET.get('store'):
            return True
    
        return False


class UserIsNotFromThisStore(permissions.BasePermission):
    message = 'Você não tem permissão para realizar essa operação.'

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.user.has_perm('user.be_admin') \
            and request.user.admin.my_store.id == int(request.GET['store']):
            return True
        elif request.user.has_perm('user.be_seller') \
            and request.user.seller.my_store.id == int(request.GET['store']):
            return True
        elif request.user.has_perm('user.be_punter') \
            and request.user.punter.my_store.id == int(request.GET['store']):			
            return True
        elif request.user.has_perm('user.be_manager') \
            and request.user.manager.my_store.id == int(request.GET['store']):		
            return True
        
        return False


class CanModifyCotation(permissions.BasePermission):
    message = "Você não tem permissão para modificar cotas."

    def has_permission(self, request, view):
        if request.user.is_superuser:								
            return True	
        if request.user.has_perm('user.be_admin'):
            return True	
        
        return False


class CanChangeStore(permissions.BasePermission):
    message = "Somente super usuários podem manipular Stores."

    def has_permission(self, request, view):
        if request.user.is_superuser:								
            return True
        
        return False
