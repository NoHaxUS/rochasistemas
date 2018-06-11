from django.db import models
from django.contrib.auth.models import User, Permission, AbstractUser, BaseUserManager
from guardian.shortcuts import assign_perm, remove_perm
from django.db.models import F, Q, When, Case
from guardian.shortcuts import get_objects_for_user
# Create your models here.

objects = models.Manager()

class CustomUser(AbstractUser):
    cellphone = models.CharField(max_length=14, verbose_name='Celular')
    email = models.EmailField(null=True, verbose_name='E-mail')

    def __str__(self):
        return self.first_name

    def full_name(self):
        return self.first_name + ' ' + self.last_name
    full_name.short_description = 'Nome Completo'

    


class NormalUser(models.Model):
    first_name = models.CharField(max_length=40, verbose_name='Nome')
    cellphone = models.CharField(max_length=14, verbose_name='Celular')

    def __str__(self):
        return self.first_name



class Seller(CustomUser):
    cpf = models.CharField(max_length=11, verbose_name='CPF')
    address = models.CharField(max_length=75, verbose_name='Endereço')
    can_sell_unlimited = models.BooleanField(default=True, verbose_name='Vender Ilimitado?')
    commission = models.FloatField(default=0, verbose_name='Comissão')
    credit_limit = models.FloatField(default=0, verbose_name='Créditos')
    my_manager = models.ForeignKey('Manager', on_delete=models.SET_NULL, related_name='manager_assoc', verbose_name='Gerente', null=True, blank=True)


    def reset_revenue(self, who_reseted_revenue):
        from core.models import Payment
        from history.models import RevenueHistorySeller

        payments = Payment.objects.filter(who_set_payment_id=self.pk, seller_was_rewarded=False)
        
        RevenueHistorySeller.objects.create(who_reseted_revenue=who_reseted_revenue,
        seller=self,
        final_revenue=self.actual_revenue(),
        actual_comission=self.commission,
        earned_value=self.net_value())

        payments.update(seller_was_rewarded=True)



    
    def full_name(self):
        return self.first_name + ' ' + self.last_name
    full_name.short_description = 'Nome Completo'

    
    def net_value(self):
        
        total_net_value = self.actual_revenue() * (self.commission / 100)
        return round(total_net_value,2)
    net_value.short_description = 'Líquido'
    net_value.cor = 'Azul'
    
    
    def actual_revenue(self):
        from core.models import BetTicket
        tickets_revenue = BetTicket.objects.filter(payment__who_set_payment_id=self.pk, payment__seller_was_rewarded=False)
        revenue_total = 0

        for ticket in tickets_revenue:
            revenue_total += ticket.value
        return revenue_total

    actual_revenue.short_description = 'Faturamento Total'



    def save(self, *args, **kwargs):
        self.clean()
        if not self.has_usable_password():	
            self.set_password(self.password) 
        super().save()


        be_seller_perm = Permission.objects.get(codename='be_seller')
        change_ticket_perm = Permission.objects.get(codename='change_betticket')
        view_managertransactions_perm = Permission.objects.get(codename='view_managertransactions')
        view_revenuehistoryseller_perm = Permission.objects.get(codename='view_revenuehistoryseller')
        view_sellersaleshistory_perm = Permission.objects.get(codename='view_sellersaleshistory')
        view_punterpayedhistory_perm = Permission.objects.get(codename='view_punterpayedhistory')
        
        self.user_permissions.add(be_seller_perm, change_ticket_perm, 
        view_managertransactions_perm, view_revenuehistoryseller_perm, 
        view_sellersaleshistory_perm, view_punterpayedhistory_perm)
        #self.user_permissions.add(chance_betticket)



    class Meta:
        verbose_name = 'Vendedor'
        verbose_name_plural = 'Vendedores'

        permissions = (
            ('be_seller', 'Be a seller, permission.'),
        )

class Punter(CustomUser):	

    def save(self, *args, **kwargs):
        self.clean()
        if not self.has_usable_password():	
            self.set_password(self.password)
        super(Punter, self).save()

    class Meta:
        verbose_name = 'Apostador'
        verbose_name_plural = 'Apostadores'


class Manager(CustomUser):
    cpf = models.CharField(max_length=11, verbose_name='CPF', null=True)
    address = models.CharField(max_length=75, verbose_name='Endereço', null=True)
    commission = models.FloatField(default=0, verbose_name='Comissão')
    credit_limit_to_add = models.FloatField(default=0, verbose_name="Crédito")


    def net_value(self):
        total_net_value = self.actual_revenue() * (self.commission / 100)
        return round(total_net_value,2)
    net_value.short_description = 'Líquido'

    def actual_revenue(self):

        manager = CustomUser.objects.get(pk=self.pk)
        sellers = get_objects_for_user(manager, 'user.set_credit_limit').order_by('-pk')

        total_revenue = 0
        for seller in sellers:
            total_revenue += seller.actual_revenue()
        return total_revenue
    actual_revenue.short_description = 'Faturamento'


    def manage_credit(self, obj):
        from history.models import ManagerTransactions

        seller = Seller.objects.get(pk=obj.pk)

        manager_before_balance = self.credit_limit_to_add
        seller_before_balance = seller.credit_limit

        diff = obj.credit_limit - seller.credit_limit
        manager_balance_after = self.credit_limit_to_add - diff

        seller_after_balance = seller.credit_limit + diff

        obj.can_sell_unlimited = seller.can_sell_unlimited

        if manager_balance_after < 0:
            return {'success': False,
            'message': 'Você não tem saldo suficiente'}
        elif obj.credit_limit < 0:
            return {'success': False,
            'message': 'Você não pode ter saldo negativo.'}
        else:
            self.credit_limit_to_add -= diff
            self.save()

            ManagerTransactions.objects.create(manager=self,
            seller=seller,
            transferred_amount=diff,
            manager_before_balance=manager_before_balance,
            manager_after_balance=manager_balance_after,
            seller_before_balance=seller_before_balance,
            seller_after_balance=seller_after_balance)

            return {'success': True,
            'message': 'Transação realizada.'}
        

    def add_set_limit_permission(self,sellers):		
        for seller in sellers:
            assign_perm('set_credit_limit',self,seller)

    def remove_set_limit_permission(self, sellers):
        for seller in sellers:
            remove_perm('set_credit_limit',self,seller)

    def save(self, *args, **kwargs):					
        if not self.has_usable_password():	
            self.set_password(self.password)

        super(Manager, self).save()
        self.clean()			

        be_manager_permission = Permission.objects.get(codename='be_manager')
        
        self.user_permissions.add(be_manager_permission)

    class Meta:
        verbose_name = 'Gerente'
        verbose_name_plural = 'Gerentes'
        permissions = (								
                ('be_manager', 'Be a manager, permission.'),
            )
