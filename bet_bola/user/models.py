from django.db import models
from django.contrib.auth.models import User, Permission, AbstractUser, BaseUserManager
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

    def __str__(self):
        return self.first_name

    def full_name(self):
        return self.first_name + ' ' + self.last_name


class Admin(CustomUser):    
    my_store = models.ForeignKey('core.Store', verbose_name='Banca', on_delete=models.CASCADE)

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
        self.is_superuser = False
        self.is_staff = False
        self.user_type = 4
        super().save()
        admin.define_default_permissions(self)


class TicketOwner(models.Model):
    first_name = models.CharField(max_length=150, verbose_name='Nome')
    cellphone = models.CharField(max_length=14, verbose_name='Celular', null=True, blank=True)   
    my_store = models.ForeignKey('core.Store', verbose_name='Banca', on_delete=models.CASCADE)     

    def __str__(self):
        return self.first_name


class Punter(CustomUser):        
    my_store = models.ForeignKey('core.Store', verbose_name='Banca', on_delete=models.CASCADE)    

    def save(self, *args, **kwargs):
        self.clean()
        if not self.password.startswith('pbkdf2'):
            self.set_password(self.password)
        self.is_superuser = False
        self.user_type = 1
        self.is_staff = True
        
        super().save()
        
        self.define_default_permissions()

    def define_default_permissions(self):

        view_ticket_perm = Permission.objects.get(codename='view_ticket')
        be_punter = Permission.objects.get(codename='be_punter')
        change_punter = Permission.objects.get(codename='change_punter')

        self.user_permissions.add(view_ticket_perm, be_punter, change_punter)

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
    my_store = models.ForeignKey('core.Store', verbose_name='Banca', on_delete=models.CASCADE)

    def reset_revenue(self, who_reseted_revenue):
        seller.reset_revenue(self, who_reseted_revenue)

    def full_name(self):
        return seller.full_name(self)
    
    def net_value(self):                
        return seller.net_value(self)

    def real_net_value(self):
        return seller.real_net_value(self)

    def see_comissions(self):
        return seller.see_comissions(self)
    
    def get_commission(self):
        return seller.get_commission(self)

    def out_money(self):        
        return seller.out_money(self)

    def actual_revenue(self):
        return seller.actual_revenue(self)

    def save(self, *args, **kwargs):
        self.clean()
        if not self.password.startswith('pbkdf2'):			
            self.set_password(self.password)
        self.is_superuser = False
        self.is_staff = False
        self.user_type = 2
        super().save()

        from utils.models import Comission
        comission = Comission.objects.filter(seller_related=self)
        if not comission:
            Comission(seller_related=self,store=self.my_store).save()
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
    my_store = models.ForeignKey('core.Store', verbose_name='Banca', on_delete=models.CASCADE)       

    def reset_revenue(self, who_reseted_revenue):        
        manager.reset_revenue(self, who_reseted_revenue)

    def out_money(self):
        return manager.out_money(self)

    def get_commission(self):
        return manager.get_commission(self)    

    def net_value(self):
        return manager.net_value(self)

    def real_net_value(self):
        return manager.real_net_value(self)    

    def net_value_before_comission(self):
        return manager.net_value_before_comission(self)

    def actual_revenue(self):
        return manager.actual_revenue(self)

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
