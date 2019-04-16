from rest_framework import permissions

class IsSuperUser(permissions.BasePermission):
	message = "Apenas contas administradoras podem efetuar esse tipo de operação."

	def has_permission(self, request, view):
		if request.user.is_superuser:			
			return True		
		return False


class StoreGiven(permissions.BasePermission):
	message = "Forneça a id da banca"
	def has_permission(self, request, view):
		store = request.GET.get('store')
		if store:
			return True
		return False


class IsSeller(permissions.BasePermission):
	message = "Apenas contas de vendedores podem efetuar esse tipo de operação."
	
	def has_permission(self, request, view):		
		if request.user.has_perm('user.be_seller'):
			return True
		if request.user.has_perm('user.be_admin') and str(user.admin.my_store.pk) == store:
			return True
		return False	


class ManagerViewPermission(permissions.BasePermission):
	message = "Você não tem permissão para essa operação."
	def has_permission(self, request, view):
		store = request.GET.get('store')
		user = request.user
		if not request.GET.get('store'):
			self.message = "Forneça a id da banca"
			return False
		if user.is_superuser:
			return True
		if user.has_perm('user.be_admin') and str(user.admin.my_store.pk) == store:
			return True
		if not request.method == 'POST':						
			if user.has_perm("user.be_manager") and request.GET.get('store'):
				if str(user.manager.my_store.pk) == str(store):
					return True
				self.message = "Administrador não pertence a essa banca"
				return False
		return False

	def has_object_permission(self, request, view, obj):
		if request.user.is_superuser:
			return True		
		return request.user.pk == obj.pk

class PunterViewPermission(permissions.BasePermission):
	message = "Você não tem permissão para essa operação."

	def has_permission(self, request, view):
		store = request.GET.get('store')
		user = request.user
		if not request.GET.get('store'):
			self.message = "Forneça a id da banca"
			return False
		if request.user.is_superuser:		
			return True
		if user.has_perm('user.be_admin') and str(user.admin.my_store.pk) == store:
			return True				
		if request.method == 'POST':
			if not store:
				self.message = "Forneça id da banca"
				return False			
			return True		
		if user.is_authenticated and ((user.has_perm('user.be_seller') and str(user.seller.my_store.pk) != str(store)) or user.has_perm('user.be_manager') and str(user.manager.my_store.pk) != str(store)):			
			self.message = "Usuario não pertence a essa banca"
			return False			
		if user.is_authenticated and ((user.has_perm('user.be_seller') and str(user.seller.my_store.pk) == str(store)) or user.has_perm('user.be_manager') and str(user.manager.my_store.pk) == str(store)):			
			return True

		return False

	def has_object_permission(self, request, view, obj):
		if request.user.is_superuser:
			return True
		elif user.has_perm('user.be_admin') and str(user.admin.my_store.pk) == store:
			return True
		else:
			if not request.GET.get('store'):
				self.message = "Forneça id da banca"
				return False		
		return request.user.pk == obj.pk


class SellerViewPermission(permissions.BasePermission):
	message = "Você não tem permissão para essa operação."

	def has_permission(self, request, view):
		store = request.GET.get('store')
		user = request.user
		if user.is_superuser:
			if not request.GET.get('store'):
				self.message = "Forneça a id da banca"
				return False
			return True
		elif user.has_perm('user.be_admin') and str(user.admin.my_store.pk) == store:
			return True
		elif user.has_perm('user.be_manager') and str(user.manager.my_store.pk) == store:
			return True
		else:
			if not store:
				self.message = "Forneça id da "
				return False			
			elif user.has_perm('user.be_manager') and str(user.manager.my_store.pk) != store:
				self.message = "Admnistrador não pertence a essa banca"
				return False
			elif user.has_perm('user.be_seller') and str(user.seller.my_store.pk) != store:
				self.message = "Vendedor não pertence a essa banca"
				return False
		return False

	def has_object_permission(self, request, view, obj):		
		if request.user.is_superuser:
			return True
		if request.user.has_perm('user.be_admin') and str(user.admin.my_store.pk) == store:
			return True
		if request.user.has_perm('user.be_manager'):
			return request.user.manager == obj.seller.my_manager

		return request.user.pk == obj.pk


# class PayManager(permissions.BasePermission):
# 	def has_permission(self, request, view):