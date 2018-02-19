from django.db import models
from django.contrib.auth.models import User, Permission, AbstractUser, BaseUserManager
# Create your models here.


class CustomUser(AbstractUser):

	def __str__(self):
		return self.first_name

	email = models.EmailField(null=True, verbose_name='E-mail')


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

	def actual_revenue(self):
		from core.models import BetTicket
		tickets_revenue = BetTicket.objects.filter(payment__who_set_payment_id=self.pk, payment__seller_was_rewarded=False)
		revenue_total = 0

		for ticket in tickets_revenue:
			revenue_total += ticket.value
		to_string = str(revenue_total)

		return "R$ " + to_string
	actual_revenue.short_description = 'Faturamento Total'

	def is_seller(self):
		return True

	def save(self, *args, **kwargs):
		self.clean()
		self.set_password(self.password)  # password encryption
		super(Seller, self).save()

		be_seller_permission = Permission.objects.get(
			codename='be_seller')
		self.user_permissions.add(be_seller_permission)


	class Meta:
		verbose_name = 'Vendedor'
		verbose_name_plural = 'Vendedores'

		permissions = (
			('be_seller', 'Be a seller, permission.'),
		)

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

	max_cotation_value = models.FloatField(default=200, verbose_name="Valor Máximo das Cotas")
	min_number_of_choices_per_bet = models.IntegerField(default=1, verbose_name="Número mínimo de escolhas por Aposta")
	max_reward_to_pay = models.FloatField(default=50000, verbose_name="Valor máximo pago pela Banca")
	min_bet_value = models.FloatField(default=1, verbose_name="Valor mínimo da aposta")	

	def __str__(self):
		return "Configuração Atual"

	def save(self, *args, **kwargs):
		from core.models import Cotation
		
		if self.max_cotation_value:
			Cotation.objects.filter(value__gt=self.max_cotation_value).update(value=self.max_cotation_value)
		self.pk = 1	
		super(GeneralConfigurations, self).save()




	class Meta:
		verbose_name = "Configurar Restrições"
		verbose_name_plural = "Configurar Restrições"


