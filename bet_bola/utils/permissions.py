from rest_framework import permissions

class General(permissions.BasePermission):
	message = "Apenas contas administradoras podem efetuar esse tipo de operação."

	def has_permission(self, request, view):
		user = request.user

		if not request.GET.get('store'):
			self.message = "Forneça a id da banca"
			return False
		if request.user.is_superuser:			
			return True
		if user.has_perm('user.be_admin') and str(user.admin.my_store.pk) == store:
			return True
		return False
