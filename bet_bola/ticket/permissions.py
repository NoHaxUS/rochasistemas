from rest_framework import permissions

class CanCreateBet(permissions.BasePermission):
	message = 'Você não tem permissão para criar Tickets.'
	def has_permission(self, request, view):
		if request.user.has_perm('user.be_seller'):
			return True
		if request.user.has_perm('user.be_punter'):
			return True
		if request.user.has_perm('user.be_admin'):
			return True
		if request.user.is_anonymous:
			return True
		if request.user.is_superuser:
			return True

		return False


class CanPayWinner(permissions.BasePermission):
	message = 'Você não pode pagar vencedores. Apenas Vendedores.'
	def has_permission(self, request, view):
		if request.user.has_perm('user.be_seller'):
			return True
		return False

	def has_object_permission(self, request, view, obj):
		if request.user.seller == obj.payment.who_paid:
			return True
		self.message = 'Você não tem permissão para pagar o ganhador desse Ticket. (Apenas o ' + request.user.seller.first_name + ')'
		return False


class CanValidateTicket(permissions.BasePermission):
	message = "Você não pode Validar Ticket(s)."

	def has_permission(self, request, view):
		if request.user.has_perm('user.be_seller') or request.user.has_perm('user.be_admin') or request.user.is_superuser:							
			return True
		return False


class CanCancelTicket(permissions.BasePermission):
	message = "Você não pode Cancelar Ticket(s)."

	def has_permission(self, request, view):
		if request.user.has_perm('user.be_seller') or request.user.has_perm('user.be_admin') or request.user.is_superuser:							
			return True
		return False

	def has_object_permission(self, request, view, obj):
		if request.user.seller == obj.payment.who_paid:
			return True
		
		self.message = "Você não tem permissão para cancelar esse Ticket(s)" + request.user.seller.first_name + ')'
		return False
		