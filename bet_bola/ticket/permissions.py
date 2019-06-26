from rest_framework import permissions
from core.exceptions import NotAllowedException

class CanToggleTicketAvailability(permissions.BasePermission):
	def has_object_permission(self, request, view, obj):
		if not request.user.is_anonymous and \
			request.user.my_store == obj.store and \
			request.user.has_perm('user.be_admin'):
			return 	True
		raise NotAllowedException(detail="Você não pode alterar a visiblidade.")
		

class CanCreateTicket(permissions.BasePermission):
	message = 'Você não tem permissão para criar Tickets.'

	def has_permission(self, request, view):
		if request.user.user_type in [2,3,4]:		
			return True
		return False
	

class CanManipulateTicket(permissions.BasePermission):
	message = 'Você não tem permissão para manipular Tickets.'

	def has_permission(self, request, view):
		if request.method in ['POST', 'GET']:
			return True
		return False


class CanPayWinner(permissions.BasePermission):
	message = 'Você não pode pagar vencedores. Apenas Vendedores.'
	def has_permission(self, request, view):
		if request.user.user_type == 2:
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
		if request.user.user_type in [2,4] or request.user.is_superuser:
			return True
		return False


class CanCancelTicket(permissions.BasePermission):
	message = "Você não pode Cancelar Ticket(s)."

	def has_permission(self, request, view):
		if request.user.user_type in [2,4] or request.user.is_superuser:
			return True
		return False

	def has_object_permission(self, request, view, obj):
		if request.user.seller == obj.payment.who_paid:
			return True
		
		self.message = "Você não tem permissão para cancelar esse Ticket(s)" + request.user.seller.first_name + ')'
		return False
		