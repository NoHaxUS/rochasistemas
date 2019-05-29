from django.db import models
from django.contrib.auth.models import User, Permission, AbstractUser
from django.db.models import F, Q, When, Case
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from .logic import manager, seller, admin

class CustomUser(AbstractUser):   
    
    USER_TYPE = (
        (0, 'Anonímo'),
        (1, 'Apostador'),
        (2, 'Vendedor'),
        (3, 'Gerente'),
        (4, 'Dono da Banca')
    )

    first_name = models.CharField(max_length=150, verbose_name='Primeiro Nome')
    cellphone = models.CharField(max_length=14, verbose_name='Celular', null=True, blank=True)
    user_type = models.IntegerField(choices=USER_TYPE, default=0, verbose_name='Tipo do Usuário')
    email = models.EmailField(null=True, blank=True, verbose_name='E-mail')
    my_store = models.ForeignKey('core.Store', verbose_name='Banca', on_delete=models.CASCADE)

    def __str__(self):
        return self.first_name

    def full_name(self):
        return self.first_name + ' ' + self.last_name


class TicketOwner(models.Model):
    first_name = models.CharField(max_length=150, verbose_name='Nome')
    cellphone = models.CharField(max_length=14, verbose_name='Celular', null=True, blank=True)   
    my_store = models.ForeignKey('core.Store', verbose_name='Banca', on_delete=models.CASCADE)     

    def __str__(self):
        return self.first_name


class Admin(CustomUser):        

    class Meta:
        verbose_name = 'Administrador'
        verbose_name_plural = 'Administrador'

        permissions = (
            ('be_admin', 'Be a admin, permission.'),
        )

    def save(self, *args, **kwargs):
        self.clean()
        if not self.password.startswith('pbkdf2'):          
            self.set_password(self.password)
        self.user_type = 4
        super().save()
        admin.define_default_permissions(self)


class Punter(CustomUser):            

    def save(self, *args, **kwargs):
        self.clean()
        if not self.password.startswith('pbkdf2'):
            self.set_password(self.password)
        self.is_superuser = False
        self.is_staff = True
        self.user_type = 1
        super().save()


    class Meta:
        verbose_name = 'Apostador'
        verbose_name_plural = 'Apostadores'

        permissions = (
            ('be_punter', 'Be a punter, permission.'),
        )


class Seller(CustomUser):
    cpf = models.CharField(max_length=11, verbose_name='CPF', null=True, blank=True)    
    address = models.CharField(max_length=75, verbose_name='Endereço', null=True, blank=True)
    can_sell_unlimited = models.BooleanField(default=False, verbose_name='Vender Ilimitado?')
    credit_limit = models.DecimalField(max_digits=30, decimal_places=2,default=0, verbose_name='Crédito')
    my_manager = models.ForeignKey('Manager', on_delete=models.SET_NULL, related_name='manager_assoc', verbose_name='Gerente', null=True, blank=True)
    can_cancel_ticket = models.BooleanField(default=False, verbose_name='Cancela Bilhete ?')
    limit_time_to_cancel = models.IntegerField(default=5, verbose_name="Tempo Limite de Cancelamento", validators=[MinValueValidator(1), MaxValueValidator(45)])


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
        if not self.password.startswith('pbkdf2'):			
            self.set_password(self.password)
        self.is_superuser = False
        self.is_staff = False
        self.user_type = 2
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
    cpf = models.CharField(max_length=11, verbose_name='CPF', null=True, blank=True)    
    address = models.CharField(max_length=75, verbose_name='Endereço', null=True, blank=True)
    commission = models.DecimalField(max_digits=30, decimal_places=2,default=0, verbose_name='Comissão', validators=[MinValueValidator(Decimal('0.01'))])
    credit_limit_to_add = models.DecimalField(max_digits=30, decimal_places=2,default=0, verbose_name="Crédito")
    can_cancel_ticket = models.BooleanField(default=True, verbose_name='Cancela Bilhete ?')
    limit_time_to_cancel = models.IntegerField(default=5, verbose_name="Tempo Limite de Cancelamento", validators=[MinValueValidator(1), MaxValueValidator(45)])
    can_sell_unlimited = models.BooleanField(default=False, verbose_name='Vender Ilimitado?')
    can_change_limit_time = models.BooleanField(default=False, verbose_name='Pode alterar tempo de Cancelamento do Cambista?')
    comission_based_on_profit = models.BooleanField(default=False, verbose_name='Calcular comissão baseado no líquido ?')

    def manage_credit(self, obj, is_new=False):
        return manager.manage_credit(self, obj, is_new)
        
    def save(self, *args, **kwargs):
        self.clean()
        if not self.password.startswith('pbkdf2'):
            self.set_password(self.password)
        self.is_superuser = False
        self.is_staff = False
        self.user_type = 3
        super().save()
        manager.define_default_permissions(self)   

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Gerente'
        verbose_name_plural = 'Gerentes'
        permissions = (								
                ('be_manager', 'Be a manager, permission.'),
        )
