from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
	message = "Você não tem permissão para essa operação. (Apenas Dono da Banca)"
	def has_permission(self, request, view):
		if request.user.has_perm('user.be_admin'):
			return True
		return False

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
		
