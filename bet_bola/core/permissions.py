from rest_framework import permissions

class General(permissions.BasePermission):
	message = "Você não tem permissão para essa operação."

	def has_permission(self, request, view):
		user = request.user
		store = request.GET.get('store')		
		
		if store:			
			if request.method == 'POST':
				return False			
			return True

		self.message = "Forneça o id da baca"
		return False


class CotationModifyPermission(permissions.BasePermission):
	message = "Você não tem permissão para essa operação."

	def has_permission(self, request, view):
		store = request.GET.get('store')
		user = request.user				
		print(user.has_perm('user.be_admin'))
		if user.is_superuser:								
			return True	
		if request.user.has_perm('user.be_admin'):
			if store:				
				if str(request.user.admin.my_store.pk) != str(store):
					self.message = "Administrador não pertence a essa banca"
					return False
				return True				
			self.message = "Forneça o id da baca"
			return False			
		return False


class StorePermission(permissions.BasePermission):
	message = "Você não tem permissão para essa operação."

	def has_permission(self, request, view):
		user = request.user
				
		if user.is_superuser:								
			return True	
		return False
