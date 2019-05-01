from rest_framework import permissions
from core.models import Store
import re

class General(permissions.BasePermission):
	message = "Você não tem permissão para essa operação."

	def has_permission(self, request, view):
		user = request.user
		store = request.GET.get('store')		
		if not store:			
			self.message = "Forneça a id da banca"
			return False
		else:			
			if not Store.objects.filter(pk=store):				
				self.message = "Banca " + str(store) + " não existe"
				return False
			if request.method in permissions.SAFE_METHODS:				
				print("@@@")
				return True
			if request.user.is_superuser:							
				return True
			if user.has_perm('user.be_admin') and str(user.admin.my_store.pk) == store:				
				return True						
			return False


class ManagerAndSellerConflict(permissions.BasePermission):
	message = "Filtrar por gerente e vendedor ao mesmo tempo não é permitido"
	def has_permission(self, request, view):
		if request.GET.get('manager') and request.GET.get('seller'):
			return False
		return True


class Date(permissions.BasePermission):
	message = "Erro ao informar data"
	def has_permission(self, request, view):
		if request.GET.get('from') and request.GET.get('to'):
			_from = re.findall("(19|20)\\d\\d[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01])", request.GET.get('from'))
			_to = re.findall("(19|20)\\d\\d[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01])", request.GET.get('to'))			
			if not _from or not _to:
				self.message = "Informe as datas no formato yyyy-mm-dd"
				return False
			return True
		return True


class Balance(permissions.BasePermission):
	message = "Você não tem permissão para essa operação."

	def has_permission(self, request, view):
		user = request.user
		store = request.GET.get('store')
		if not store:
			self.message = "Forneça a id da banca"
			return False
		else:
			if not Store.objects.filter(pk=store):
				self.message = "Banca " + str(store) + " não existe"
				return False
			if request.user.is_superuser:			
				return True
			if user.has_perm('user.be_admin') and str(user.admin.my_store.pk) == store:
				return True
			if user.has_perm('user.be_seller') and str(user.admin.my_store.pk) == store:
				return True
			return False