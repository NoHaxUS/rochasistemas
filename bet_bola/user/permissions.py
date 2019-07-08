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


class BaseUserPermission(permissions.BasePermission):
	message = "Você não tem permissão para essa operação."
	user_types = []

	def has_permission(self, request, view):
		if request.method in permissions.SAFE_METHODS:
			return True
		if not request.user.is_anonymous:
			if request.user.user_type in self.user_types:			
				return True		
		raise NotAllowedException(detail=self.message)
	
	def has_object_permission(self, request, view, obj):		
		if not request.user.is_anonymous:
			if request.user.user_type in self.user_types:
				return True
		return False


class IsAdmin(BaseUserPermission):	
	user_type = [4]	


class IsManager(BaseUserPermission):
	user_type = [3]


class IsSeller(BaseUserPermission):
	user_type = [2]


class IsPunter(BaseUserPermission):
	user_type = [1]


class IsAdminOrManager(BaseUserPermission):
	user_types = [3,4]


class AlterSellerPermission(permissions.BasePermission):
	message = "Você não tem permissão para essa operação."

	def has_permission(self, request, view):				
		if request.user.user_type in [3,4]:			
			return True				
		raise NotAllowedException(detail=self.message)
	
	def has_object_permission(self, request, view, obj):
		if request.user.user_type == 4:
			return True
		if obj.my_manager and request.user.pk == obj.my_manager.pk:
			return True		
		raise NotAllowedException(detail=self.message)