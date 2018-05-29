from django.db import models
from django.contrib.auth.models import User, Permission, AbstractUser, BaseUserManager
from guardian.shortcuts import assign_perm, remove_perm
from django.db.models import F, Q, When, Case
# Create your models here.


class CustomUser(AbstractUser):
    cellphone = models.CharField(max_length=14, verbose_name='Celular')

    def __str__(self):
        return self.first_name

    email = models.EmailField(null=True, verbose_name='E-mail')


class NormalUser(models.Model):
    first_name = models.CharField(max_length=40, verbose_name='Nome')
    cellphone = models.CharField(max_length=14, verbose_name='Celular')

    def __str__(self):
        return self.first_name



class Seller(CustomUser):
    cpf = models.CharField(max_length=11, verbose_name='CPF')
    address = models.CharField(max_length=75, verbose_name='Endereço')
    can_sell_unlimited = models.BooleanField(default=True)
    credit_limit = models.FloatField(default=0, verbose_name='Créditos')


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
        if not self.has_usable_password():	
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
            ('set_credit_limit', 'Set the credit limit value'),
        )

class Punter(CustomUser):	

    def save(self, *args, **kwargs):
        self.clean()
        if not self.has_usable_password():	
            self.set_password(self.password)  # password encryption
        super(Punter, self).save()

    class Meta:
        verbose_name = 'Apostador'
        verbose_name_plural = 'Apostadores'


class Manager(CustomUser):
    cpf = models.CharField(max_length=11, verbose_name='CPF', null=True)
    address = models.CharField(max_length=75, verbose_name='Endereço', null=True)
    credit_limit_to_add = models.FloatField(default=0, verbose_name="Crédito")

    def transfer_credit_limit(self,seller,value):
        if self.has_perm('set_credit_limit', seller):
            if value <= self.credit_limit_to_add:
                seller.credit_limit += value
                self.credit_limit_to_add -= value
                self.save()
                seller.save()
                            
                return 'Valor adicionado com sucesso.'
            else:
                return 'Voce possui créditos suficientes para essa transfarência.'

        return 'Você não tem permissão para adicionar credito a esse usuário.'

    def add_set_limit_permission(self,sellers):		
        for seller in sellers:
            assign_perm('set_credit_limit',self,seller)

    def remove_set_limit_permission(self, sellers):
        for seller in sellers:
            remove_perm('set_credit_limit',self,seller)

    def save(self, *args, **kwargs):					
        if not self.has_usable_password():	
            self.set_password(self.password)  # password encryption

        super(Manager, self).save()
        self.clean()			

        be_manager_permission = Permission.objects.get(
                codename='be_manager')
        self.user_permissions.add(be_manager_permission)

    class Meta:
        verbose_name = 'Gerente'
        verbose_name_plural = 'Gerentes'
        permissions = (								
                ('be_manager', 'Be a manager, permission.'),
            )



class GeneralConfigurations(models.Model):

    max_cotation_value = models.FloatField(default=200, verbose_name="Valor Máximo das Cotas")
    min_number_of_choices_per_bet = models.IntegerField(default=1, verbose_name="Número mínimo de escolhas por Aposta")
    max_reward_to_pay = models.FloatField(default=50000, verbose_name="Valor máximo pago pela Banca")
    min_bet_value = models.FloatField(default=1, verbose_name="Valor mínimo da aposta")
    percentual_reduction = models.IntegerField(default=100, verbose_name="Redução Percentual")

    def __str__(self):
        return "Configuração Atual"

    def save(self, *args, **kwargs):
        from core.models import Game
        
        self.pk = 1

        able_games = Game.objects.able_games()

        for game in able_games:
            game.cotations.update(value=F('original_value') * round((self.percentual_reduction / 100), 2) )
            game.cotations.update(value=Case(When(value__lt=1,then=1.01),default=F('value')))
            game.cotations.filter(value__gt=self.max_cotation_value).update(value=self.max_cotation_value)
        #Cotation.objects.update(value=F('original_value') * round((self.percentual_reduction / 100), 2) )
        #Cotation.objects.update(value=Case(When(value__lt=1,then=1.01),default=F('value')))

        
        #if self.max_cotation_value:
        #    Cotation.objects.filter(value__gt=self.max_cotation_value).update(value=self.max_cotation_value)

        super(GeneralConfigurations, self).save()


    class Meta:
        verbose_name = "Configurar Restrições"
        verbose_name_plural = "Configurar Restrições"


