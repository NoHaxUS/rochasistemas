from django.db import models
from django.contrib.auth.models import User,Permission
# Create your models here.

class Generic_User(User):
	mobile_phone = models.CharField(max_length=25)
	birthday = models.DateTimeField(null=True)
	
	class Meta:
		abstract=True


class Seller(Generic_User):
	cpf = models.CharField(max_length=11)
	address = models.CharField(max_length=75)

	def is_seller(self):
		return True

	def save(self, *args, **kwargs):
		self.clean()
		self.set_password(self.password) #password encryption 
		super(Seller, self).save()
		
		payment_permission = Permission.objects.get(codename='can_validate_payment')
		reward_permission = Permission.objects.get(codename='can_reward')
		self.user_permissions.add(payment_permission)
		self.user_permissions.add(reward_permission)

	class Meta:
		verbose_name = 'Vendedor'
		verbose_name_plural = 'Vendedores'

class Punter(Generic_User):
	cellphone = models.CharField(max_length=14, default='0')

	def save(self, *args, **kwargs):
		self.clean()
		self.set_password(self.password) #password encryption 
		super(Punter, self).save()

	class Meta:
		verbose_name = 'Apostador'
		verbose_name_plural = 'Apostadores'