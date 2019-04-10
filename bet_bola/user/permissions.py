from rest_framework import permissions

class IsSuperUser(permissions.BasePermission):
	message = "Apenas contas administradoras podem efetuar esse tipo de operação."

	def has_permission(self, request, view):
		if request.user.is_superuser:			
			return True
		return False


class IsSeller(permissions.BasePermission):
	message = "Apenas contas de vendedores podem efetuar esse tipo de operação."
	
	def has_permission(self, request, view):		
		if request.user.has_perm('user.be_seller'):
			return True
		return False


class General(permissions.BasePermission):
	message = "Você não tem permissão para essa operação."

	def has_permission(self, request, view):		
		if request.method in permissions.SAFE_METHODS or request.user.is_superuser:
			return True		
		return False


class SellerViewPermission(permissions.BasePermission):
	message = "Você não tem permissão para essa operação."

	def has_permission(self, request, view):
		if request.method in permissions.SAFE_METHODS or request.user.is_superuser or request.user.has_perm('user.be_manager'):
			return True		
		return False



# class IsManager(permissions.BasePermission):
# 	def has_permission(self, request, view):		
# 		if request.user.has_perm('user.be_manager'):
# 			return True		
# 		return False

# class IsSeller(permissions.BasePermission):	
# 	message = 'Usuário não é vendedor'

# 	def has_permission(self, request, view):		
# 		if request.user.has_perm('user.be_seller'):
# 			return True
# 		return False

# class IsPunter(permissions.BasePermission):	
# 	message = 'Usuário não é apostador'

# 	def has_permission(self, request, view):		
# 		if request.user.has_perm('user.be_punter'):
# 			return True
# 		return False


# class IsAnonymous(permissions.BasePermission):	
	
# 	def has_permission(self, request, view):		
# 		if request.user.is_anonymous:
# 			return True
# 		return False