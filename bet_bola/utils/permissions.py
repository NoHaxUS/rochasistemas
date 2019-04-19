from rest_framework import permissions
from core.models import Store

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
			if request.user.is_superuser:			
				return True
			if user.has_perm('user.be_admin') and str(user.admin.my_store.pk) == store:
				return True
			return False


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