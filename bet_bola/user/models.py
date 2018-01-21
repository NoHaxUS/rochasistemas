from django.db import models
from django.contrib.auth.models import User, Permission, AbstractUser, BaseUserManager
# Create your models here.


class CustomUser(AbstractUser):

	def __str__(self):
		return self.first_name

	email = models.EmailField(null=True,verbose_name='E-mail')



class RandomUser(models.Model):
	first_name = models.CharField(max_length=40, verbose_name='Nome')
	cellphone = models.CharField(max_length=14, verbose_name='Celular')

	def __str__(self):
		return self.first_name



class Seller(CustomUser):
	cpf = models.CharField(max_length=11, verbose_name='CPF')
	address = models.CharField(max_length=75, verbose_name='Endereço')
	cellphone = models.CharField(max_length=14, verbose_name='Celular')


	def full_name(self):
		return self.first_name + ' ' + self.last_name
	full_name.short_description = 'Nome Completo'

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

	cellphone = models.CharField(max_length=14, verbose_name='Celular')


	def save(self, *args, **kwargs):
		self.clean()
		self.set_password(self.password)  # password encryption
		super(Punter, self).save()

	class Meta:
		verbose_name = 'Apostador'
		verbose_name_plural = 'Apostadores'



class GeneralConfigurations(models.Model):

	max_cotation_value = models.FloatField(null=True, verbose_name="Valor Máximo das Cotas")
	min_number_of_choices_per_bet = models.IntegerField(default=0, verbose_name="Número mínimo de escolhas por Aposta")
	max_reward_to_pay = models.FloatField(null=True, verbose_name="Valor máximo pago pela Banca")
	min_bet_value = models.FloatField(null=True, verbose_name="Valor mínimo da aposta")


	def __str__(self):
		return "Configuração Atual"

	def save(self, *args, **kwargs):

		self.pk = 1	
		super(GeneralConfigurations, self).save()




	class Meta:
		verbose_name = "Configurar Restrições"
		verbose_name_plural = "Configurar Restrições"


