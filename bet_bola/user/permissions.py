from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
	message = "Você não tem permissão para essa operação. (Apenas Dono da Banca)"
	def has_permission(self, request, view):
		if request.user.has_perm('user.be_admin'):
			return True
		return False
