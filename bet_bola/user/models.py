from django.db import models
from django.contrib.auth.models import User, Permission, AbstractUser
from django.db.models import F, Q, When, Case
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from .logic import manager, seller, admin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import UserManager

def define_password(self):
    if not self.password.startswith('pbkdf2'):			
        self.set_password(self.password)


class CustomUserManager(UserManager):
    def create_superuser(self, username, email, password, **extra_fields):
        from core.models import Store
        try:
            store = Store.objects.get(pk=extra_fields['my_store'])
            extra_fields['my_store'] = store
        except Store.DoesNotExist:
            raise ValueError("Essa Banca não existe")
        
        return super().create_superuser(username, email, password, **extra_fields)

class CustomUser(AbstractUser):   
    
    USER_TYPE = (
        (0, 'Anonímo'),
        (1, 'Apostador'),
        (2, 'Cambista'),
        (3, 'Gerente'),
        (4, 'Dono da Banca')
    )

    objects = CustomUserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['my_store', 'email']

    first_name = models.CharField(max_length=150, verbose_name='Primeiro Nome')
    cellphone = models.CharField(max_length=14, null=True, blank=True, verbose_name='Celular')
    user_type = models.IntegerField(choices=USER_TYPE, default=0, verbose_name='Tipo do Usuário')
    email = models.EmailField(unique=True, verbose_name='E-mail')
    my_store = models.ForeignKey('core.Store', on_delete=models.CASCADE, verbose_name='Banca')

    def __str__(self):
        return self.username


class Admin(CustomUser):        

    class Meta:
        verbose_name = 'Administrador'
        verbose_name_plural = 'Administrador'

        permissions = (
            ('be_admin', 'Be a admin, permission.'),
        )

    def manage_user_credit(self, user, value):
        return admin.manage_user_credit(self, user, value)

    def save(self, *args, **kwargs):
        self.clean()
        self.user_type = 4
        define_password(self)
        super().save()
        admin.define_default_permissions(self)


class Punter(CustomUser):            

    def save(self, *args, **kwargs):
        self.clean()
        self.user_type = 1
        define_password(self)
        super().save()


    class Meta:
        verbose_name = 'Apostador'
        verbose_name_plural = 'Apostadores'

        permissions = (
            ('be_punter', 'Be a punter, permission.'),
        )


class Seller(CustomUser):
    cpf = models.CharField(max_length=17, null=True, blank=True, verbose_name="CPF")
    address = models.CharField(max_length=75, null=True, blank=True, verbose_name="Endereço")
    can_sell_unlimited = models.BooleanField(default=False, verbose_name='Vender Ilimitado?')
    credit_limit = models.DecimalField(max_digits=30, decimal_places=2,default=0, verbose_name='Crédito')
    my_manager = models.ForeignKey('Manager', null=True, blank=True, on_delete=models.SET_NULL, related_name='manager_assoc', verbose_name='Gerente')
    can_cancel_ticket = models.BooleanField(default=False, verbose_name='Cancela Bilhete ?')
    limit_time_to_cancel = models.IntegerField(default=5, verbose_name="Tempo Limite de Cancelamento", validators=[MinValueValidator(1), MaxValueValidator(45)])


    def toggle_is_active(self):
        self.is_active = not self.is_active
        self.save()

    def alter_credit(self, credit):
        self.credit_limit += credit
        self.save()

    def toggle_can_sell_unlimited(self):
        self.can_sell_unlimited = not self.can_sell_unlimited
        self.save()

    def toggle_can_cancel_ticket(self):
        self.can_cancel_ticket = not self.can_cancel_ticket
        self.save()

    def save(self, *args, **kwargs):
        self.clean()
        self.user_type = 2
        define_password(self)
        super().save()
        seller.define_default_permissions(self)        


    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Cambista'
        verbose_name_plural = 'Cambistas'

        permissions = (
            ('be_seller', 'Be a seller, permission.'),
        )


class Manager(CustomUser):
    cpf = models.CharField(max_length=17, null=True, blank=True, verbose_name="CPF")    
    address = models.CharField(max_length=75, null=True, blank=True, verbose_name='Endereço')
    credit_limit = models.DecimalField(max_digits=30, decimal_places=2,default=0, verbose_name="Crédito")
    can_cancel_ticket = models.BooleanField(default=True, verbose_name='Cancela Bilhete ?')
    limit_time_to_cancel = models.IntegerField(default=5, verbose_name="Tempo Limite de Cancelamento", validators=[MinValueValidator(1), MaxValueValidator(45)])
    can_sell_unlimited = models.BooleanField(default=False, verbose_name='Vender Ilimitado?')
    can_change_limit_time = models.BooleanField(default=False, verbose_name='Pode alterar tempo de Cancelamento do Cambista?')
    can_modify_seller = models.BooleanField(default=False, verbose_name='Pode alterar ou deletar Cambista?')
    can_modify_seller_comissions = models.BooleanField(default=False, verbose_name='Pode alterar comissões de Cambista?')
    comission_based_on_profit = models.BooleanField(default=False, verbose_name='Calcular comissão baseado no líquido ?')
    can_close_cashier = models.BooleanField(default=True, verbose_name='Pode fechar o caixa ?')

    
    def toggle_is_active(self):
        self.is_active = not self.is_active
        self.save()
        
    def toggle_can_close_cashier(self):        
        self.can_close_cashier = not self.can_close_cashier
        self.save()

    def toggle_can_modify_seller_comissions(self):        
        self.can_modify_seller_comissions = not self.can_modify_seller_comissions                
        self.save()

    def toggle_can_sell_unlimited(self):        
        self.can_sell_unlimited = not self.can_sell_unlimited        
        self.save()

    def toggle_can_modify_seller(self):
        self.can_modify_seller = not self.can_modify_seller
        self.save()

    def toggle_can_cancel_ticket(self):
        self.can_cancel_ticket = not self.can_cancel_ticket
        self.save()

    def toggle_can_sell_unlimited(self):
        self.can_sell_unlimited = not self.can_sell_unlimited
        self.save()

    def toggle_can_change_limit_time(self):
        self.can_change_limit_time = not self.can_change_limit_time
        self.save()

    def toggle_comission_based_on_profit(self):
        self.comission_based_on_profit = not self.comission_based_on_profit
        self.save()

    def manage_seller_credit(self, seller, value):
        return manager.manage_seller_credit(self, seller, value)
        
    def alter_credit(self, credit):
        self.credit_limit += credit
        self.save()
        
    def save(self, *args, **kwargs):
        self.clean()
        self.user_type = 3
        define_password(self)
        super().save()
        manager.define_default_permissions(self)   

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Gerente'
        verbose_name_plural = 'Gerentes'
        permissions = (								
                ('be_manager', 'Be a manager, permission.'),
        )


class TicketOwner(models.Model):
    first_name = models.CharField(max_length=150, verbose_name='Nome')
    cellphone = models.CharField(max_length=14, verbose_name='Celular', null=True, blank=True)   
    my_store = models.ForeignKey('core.Store', verbose_name='Banca', on_delete=models.CASCADE)     

    def __str__(self):
        return self.first_name