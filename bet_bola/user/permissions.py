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
	user_type = None

	def has_permission(self, request, view):				
		if request.user.user_type == self.user_type:			
			return True		
		raise NotAllowedException(detail=self.message)
	
	def has_object_permission(self, request, view, obj):
		if request.user.user_type == self.user_type:
			return True
		return False


class IsAdmin(BaseUserPermission):	
	user_type = 4	


class IsManager(BaseUserPermission):
	user_type = 3


class IsSeller(BaseUserPermission):
	user_type = 2


class IsPunter(BaseUserPermission):
	user_type = 1


class AlterCreditPermission(permissions.BasePermission):
	message = "Você não tem permissão para essa operação."

	def has_permission(self, request, view):				
		if request.user.user_type in [3,4]:			
			return True				
		raise NotAllowedException(detail=self.message).get_full_details()
	
	def has_object_permission(self, request, view, obj):
		if request.user.user_type == 4:
			return True
		if obj.my_manager and request.user.pk == obj.my_manager.pk:
			return True		
		raise NotAllowedException(detail=self.message)