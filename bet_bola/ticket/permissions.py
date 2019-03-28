from rest_framework import permissions


class CreateBet(permissions.BasePermission):
	message = "Desculpe, Contas administradoras ou Gerentes não são apropriados para criarem apostas. Use contas normais ou conta de vendedor."

	def has_permission(self, request, view):
		if request.user.is_superuser or request.user.has_perm("user.be_manager"):			
			return False
		return True