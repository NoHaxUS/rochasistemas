from rest_framework import permissions


class CreateBet(permissions.BasePermission):
	message = "Desculpe, Contas administradoras ou Gerentes não são apropriados para criarem apostas. Use contas normais ou conta de vendedor."

	def has_permission(self, request, view):		
		if request.method in permissions.SAFE_METHODS:			
			if not request.GET.get('store'):				
				self.message = "Forneça a id da loja"
				return False
			return True
		elif not request.GET.get('store'):
			self.message = "Forneça a id da loja"
			return False
		elif request.user.is_superuser or request.user.has_perm("user.be_manager"):			
			return False
		elif request.user.has_perm('user.be_admin') and str(user.admin.my_store.pk) == store:
			return False			
		elif request.user.has_perm('user.be_seller') and str(request.user.seller.my_store.id) != str(request.GET['store']):
			self.message = "Usuario não é pertencente a esta banca"
			return False
		elif request.user.has_perm('user.be_punter') and str(request.user.punter.my_store.id) != str(request.GET['store']):				
			self.message = "Usuario não é pertencente a esta banca"				
			return False			
		return True

	def has_object_permission(self, request, view, obj):
		if request.method in permissions.SAFE_METHODS:
			return True
		else:
			if request.user.has_perm('user.be_seller') and request.user.seller.my_store == obj.store:
				return True
			if request.user.has_perm('user.be_manager') and request.user.manager.my_store == obj.store:
				return True
			if request.user.is_superuser:
				return True			
			return False


class PayWinnerPermission(permissions.BasePermission):
	def has_permission(self, request, view):
		if request.user.has_perm('user.be_seller'):
			if not str(request.GET['store']):
				self.message = "Entrada da banca não inserida"				
				return False
			if str(request.user.seller.my_store.id) != str(request.GET['store']):
				self.message = "Ticket não é pertencente a esta banca"
				return False
		self.message = "Usuário não é vendedor"
		return True


class ValidateTicketPermission(permissions.BasePermission):
	message = "Você não tem permissão para essa operação."

	def has_permission(self, request, view):
		store = request.GET.get('store')
		user = request.user

		if request.user.has_perm('user.be_seller'):
			if not store:
				self.message = "Forneça a id da loja"
				return False
			if str(user.seller.my_store.id) != str(store):
				self.message = "Usuário não é vendedor desta banca"
				return False					
			return True		
		self.message = "Usuário não é vendedor"
		return False


class CancelarTicketPermission(permissions.BasePermission):
	message = "Você não tem permissão para essa operação."

	def has_permission(self, request, view):
		store = request.GET.get('store')
		user = request.user		
		if request.user.has_perm('user.be_seller'):
			if not store:
				self.message = "Forneça a id da loja"
				return False
			if str(user.seller.my_store.id) != str(store):
				self.message = "Usuário não é vendedor desta banca"
				return False					
			return True		
		self.message = "Usuário não é vendedor"
		return False

	def has_object_permission(self, request, view, obj):		
		if request.user.has_perm('user.be_seller'):
			if request.user.pk == obj.seller.pk:
				return True
			self.message = "Vendedor não tem permissão sobre esse ticket" 
			return False
		self.message = "Usuário não é vendedor"
		return False