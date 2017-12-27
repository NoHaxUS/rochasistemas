from django.db import models
from django.contrib.auth.models import User, Permission, AbstractUser, BaseUserManager
# Create your models here.


class CustomUserManager(BaseUserManager):

	use_in_migrations = True

	def _create_user(self, username, password, **extra_fields):
		"""Create and save a User with the given username and password."""
		if not username:
			raise ValueError('The given username must be set')
		user = self.model(username=username, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, username, password, **extra_fields):
		"""Create and save a regular User with the given username and password."""
		extra_fields.setdefault('is_staff', False)
		extra_fields.setdefault('is_superuser', False)
		return self._create_user(username, password, **extra_fields)

	def create_superuser(self, username, password, **extra_fields):
		"""Create and save a SuperUser with the given username and password."""
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)

		if extra_fields.get('is_staff') is not True:
			raise ValueError('Superuser must have is_staff=True.')
		if extra_fields.get('is_superuser') is not True:
			raise ValueError('Superuser must have is_superuser=True.')

		return self._create_user(username, password, **extra_fields)

		def normalize_email(email):
			return email

		def a():
			pass




class CustomUser(AbstractUser):

	email = models.EmailField(null=True)
	#objects = CustomUserManager()


class Seller(CustomUser):
	cpf = models.CharField(max_length=11)
	address = models.CharField(max_length=75)

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
