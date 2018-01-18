from django.db import models
from django.contrib.auth.models import User, Permission, AbstractUser, BaseUserManager
# Create your models here.


class CustomUser(AbstractUser):

	def __str__(self):
		return self.first_name
		

	email = models.EmailField(null=True)


class RandomUser(models.Model):
	first_name = models.CharField(max_length=40)
	cellphone = models.CharField(max_length=14)

	def __str__(self):
		return self.first_name


class Seller(CustomUser):
	cpf = models.CharField(max_length=11)
	address = models.CharField(max_length=75)
	cellphone = models.CharField(max_length=14)

	def is_seller(self):
		return True

	def save(self, *args, **kwargs):
		self.clean()
		self.set_password(self.password)  # password encryption
		super(Seller, self).save()

		payment_permission = Permission.objects.get(
			codename='can_validate_payment')
		reward_permission = Permission.objects.get(codename='can_reward')
		self.user_permissions.add(payment_permission)
		self.user_permissions.add(reward_permission)

	class Meta:
		verbose_name = 'Vendedor'
		verbose_name_plural = 'Vendedores'


class Punter(CustomUser):

	cellphone = models.CharField(max_length=14)


	def save(self, *args, **kwargs):
		self.clean()
		self.set_password(self.password)  # password encryption
		super(Punter, self).save()

	class Meta:
		verbose_name = 'Apostador'
		verbose_name_plural = 'Apostadores'
