from rest_framework import permissions

class General(permissions.BasePermission):
	message = "Você não tem permissão para essa operação."

	def has_permission(self, request, view):
		user = request.user
		store = request.GET.get('store')		
		if store:					
			if user.has_perm('user.be_seller') and str(user.seller.my_store.pk) == str(store):
				return True
			if user.has_perm('user.be_manager') and str(user.manager.my_store.pk) == str(store):
				return True
			if user.is_superuser:
				return True
			if user.has_perm('user.be_admin') and str(user.admin.my_store.pk) == store:
				return True
			return False

		self.message = "Forneça o id da baca"
		return False
