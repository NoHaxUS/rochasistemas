from rest_framework import permissions
from core.exceptions import NotAllowedException

class IsSuperUser(permissions.BasePermission):
	message = "Você não tem permissão para essa operação. (Apenas Super Usuários)"
	def has_permission(self, request, view):
		if request.user.is_superuser:
			return True
		return False

	def has_object_permission(self, request, view, obj):
		if request.user.is_superuser:
			return True
		return False

class AdminUserViewPermission(permissions.BasePermission):
	message = "Você não tem permissão para essa operação. (Apenas Super Usuários)"
	def has_permission(self, request, view):
		if request.user.is_superuser or request.user.user_type == 4:
			return True
		return False

	def has_object_permission(self, request, view, obj):
		if request.user.is_superuser or request.user.pk == obj.pk:
			return True
		return False


class BaseUserPermission(permissions.BasePermission):
	message = "Você não tem permissão para essa operação."
	user_types = []

	def has_permission(self, request, view):						
		if request.method in permissions.SAFE_METHODS and request.user.is_authenticated:			
			return True
		if not request.user.is_anonymous:									
			if request.user.user_type in self.user_types:			
				return True		
		raise NotAllowedException(detail=self.message)
	
	def has_object_permission(self, request, view, obj):		
		if request.method in permissions.SAFE_METHODS:
			return True
		if not request.user.is_anonymous:
			if request.user.user_type in self.user_types:
				return True
		return False


class IsAdmin(BaseUserPermission):	
	user_types = [4]


class IsManager(BaseUserPermission):
	user_types = [3]


class IsSeller(BaseUserPermission):
	user_types = [2]


class IsPunter(BaseUserPermission):
	user_types = [1]


class IsAdminOrManager(BaseUserPermission):
	user_types = [3, 4]


class IsAdminOrManagerOrSeller(BaseUserPermission):
	user_types = [2, 3, 4]


class AlterSellerPermission(permissions.BasePermission):
	message = "Você não tem permissão para essa operação."

	def has_permission(self, request, view):				
		if request.user.user_type in [2,3,4]:			
			return True				
		raise NotAllowedException(detail=self.message)
	
	def has_object_permission(self, request, view, obj):		
		if request.user.user_type == 4:
			return True
		if obj.pk == request.user.pk:
			return True
		if obj.my_manager and request.user.pk == obj.my_manager.pk and request.user.manager.can_modify_seller:
			return True		
		raise NotAllowedException(detail=self.message)


class AlterSellerComissionsPermission(permissions.BasePermission):
	message = "Você não tem permissão para essa operação."

	def has_permission(self, request, view):				
		if request.user.user_type in [3,4]:			
			return True				
		raise NotAllowedException(detail=self.message)
	
	def has_object_permission(self, request, view, obj):		
		if request.user.user_type == 4:
			return True
		if obj.seller_related.my_manager and request.user.pk == obj.seller_related.my_manager.pk and request.user.manager.can_modify_seller_comissions:
			return True		
		raise NotAllowedException(detail=self.message)