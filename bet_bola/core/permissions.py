from rest_framework import permissions

class StoreIsRequired(permissions.BasePermission):
	def has_permission(self, request, view):
		if not request.GET.get('store'):
			self.message = "ID da Banca Obrigatório"
			return False
		return True


class UserIsNotFromThisStore(permissions.BasePermission):
	def has_permission(self, request, view):

		if request.user.is_superuser:
			return True
		if request.user.has_perm('user.be_admin') and str(request.user.admin.my_store.id) != str(request.GET['store']):			
			self.message = "Usuario não é pertencente a esta banca"
			return False
		elif request.user.has_perm('user.be_seller') and str(request.user.seller.my_store.id) != str(request.GET['store']):			
			self.message = "Usuario não é pertencente a esta banca"
			return False
		elif request.user.has_perm('user.be_punter') and str(request.user.punter.my_store.id) != str(request.GET['store']):				
			self.message = "Usuario não é pertencente a esta banca"				
			return False			
		elif request.user.has_perm('user.be_manager') and str(request.user.manager.my_store.id) != str(request.GET['store']):				
			self.message = "Usuario não é pertencente a esta banca"				
			return False			

		return True


class GamePermission(permissions.BasePermission):
	message = "Insira game_id"

	def has_permission(self, request, view):
		if not request.GET.get('game_id'):
			return False
		return True


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
