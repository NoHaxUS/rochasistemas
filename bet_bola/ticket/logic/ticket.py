from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
import utils.timezone as tzlocal


def get_punter_name(self):
    if self.user:
        return self.user.first_name
    elif self.normal_user:
        return self.normal_user.first_name    

def hide_ticket(self):
    self.visible = False
    self.save()
    return {"message" :"Jogo "+ str(self.pk) +" Ocultado."}

def show_ticket(self):
    self.visible = True
    self.save()
    return {"message" :"Jogo "+ str(self.pk) +" Exibido."}

def get_ticket_link(self):
    from django.utils.safestring import mark_safe
    link = '<a href="/ticket/'+str(self.pk) + '/" class="consult">Consultar<a/>'
    return mark_safe(link)    

def seller_related(self):
    if self.payment:
        return self.payment.who_paid    

def cancel_ticket(self, user):
    from history.models import TicketCancelationHistory
    from core.models import Store

    if not self.payment or not self.reward:
        return {'success':False,
            'message':'O Ticket '+ str(self.pk)+ ' é inválido.'}
    
    who_cancelled  = str(user.pk) + ' - ' + user.username
    if not self.status == 0:
        return {'success':False,
            'message':' Ticket '+ str(self.pk)+ ' não cancelado, pois não está aguardando resultados.'}
    
    if not self.payment.status == 2:
        return {'success':False,
            'message':'O Ticket '+ str(self.pk) +' não está Pago para ser cancelado.'}

    if user.has_perm('user.be_seller') and not user.is_superuser:
        if self.payment.date + timezone.timedelta(minutes=int(user.seller.limit_time_to_cancel)) < tzlocal.now():
            return {'success':False,
                'message':' Tempo limite para cancelar o Ticket '+ str(self.pk) +' excedido.'}

    if user.has_perm('user.be_manager') and not user.is_superuser:
        if self.payment.date + timezone.timedelta(minutes=int(user.manager.limit_time_to_cancel)) < tzlocal.now():
            return {'success':False,
                'message':' Tempo limite para cancelar o Ticket '+ str(self.pk) +' excedido.'}

    if user != self.payment.who_paid:
        return {'success':False,
                'message':'Vendedor ' + user.first_name+ ' não tem permissão para cancelar este ticket.'}
    
    seller = self.payment.who_paid
    if not seller.can_sell_unlimited:
        seller.credit_limit += self.value
        seller.save()

    self.payment.status = 5
    self.payment.date = None
    # self.payment.seller_was_rewarded = True
    self.payment.save()
    self.save()

    TicketCancelationHistory.objects.create(who_cancelled=who_cancelled,
    ticket_cancelled=self,
    seller_of_payed=seller,
    store=self.store)

    return {'success':True,
        'message':'O Ticket '+ str(self.pk) +' foi cancelado.'}

def validate_ticket(self, user):
    from history.models import SellerSalesHistory
    from core.models import Store      
    from user.models import Seller              
    
    if self.cotation_sum() * self.value >= self.store.config.alert_bet_value:
        bet_reward_value = str(round((self.cotation_sum() * self.value),2))
        if self.store.email:
            subject = 'Alerta de aposta'
            message = 'Uma aposta com recompensa no valor de R$' + bet_reward_value + ' foi efetuada em sua plataforma'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [self.store.email,]
            send_mail( subject, message, email_from, recipient_list )
        
    if not self.payment or not self.reward:
        return {'success':False,
            'message':'O Ticket '+ str(self.pk)+ ' é inválido.'}
    
    if not self.payment.status == 0:
        return {'success':False,
            'message':'O Ticket '+ str(self.pk) +' não está Aguardando Pagamento.'}

    if not self.status == 0:
        return {'success':False,
            'message':'O Ticket '+ str(self.pk) +' não está Aguardando Resultados.'}

    for cotation in self.cotations.all():
        if cotation.game.start_date < tzlocal.now():
            return {'success':False,
            'message':'O Ticket '+ str(self.pk) +' não pode ser pago, pois tem jogo(s) que já começaram.'}

    seller_before_balance = 0
    seller_after_balance= 0
        
    if not user.seller.can_sell_unlimited:
        if self.value > user.seller.credit_limit:                
            return {'success':False,
            'message':'Você não tem saldo suficiente para pagar o Ticket: ' + str(self.pk)}
        seller_before_balance = user.seller.credit_limit
        user.seller.credit_limit -= self.value
        seller_after_balance = user.seller.credit_limit
        user.seller.save()
                
    self.save()
    self.payment.status = 2
    self.payment.date = tzlocal.now()
    self.payment.who_paid = Seller.objects.get(pk=user.pk)
    self.payment.save()

    SellerSalesHistory.objects.create(seller=user.seller,
    bet_ticket=self,
    value=self.value,
    seller_before_balance=seller_before_balance,
    seller_after_balance=seller_after_balance,
    store=self.store)
    
    return {'success':True,
        'message':'Ticket '+ str(self.pk) +' Pago com Sucesso.'}

def pay_winner_punter(self, user):
    from history.models import PunterPayedHistory
    from user.models import Seller
    from ticket.models import Ticket, Payment

    if not self.payment or not self.reward:
        return {'success':False,
            'message':'O Ticket '+ str(self.pk)+ ' é inválido.'}
            
    if not self.status == Ticket.TICKET_STATUS['Venceu']:   
        return {'success':False,
            'message':'O Ticket '+ str(self.pk) +' não Venceu'}    

    if not self.payment.status == Payment.PAYMENT_STATUS[1][1]:
        return {'success':False,
            'message':'O Ticket '+ str(self.pk) +' não foi Pago.'}

    if not self.payment.who_paid.pk == user.pk:
        return {'success':False,
            'message':'Você só pode recompensar apostas pagas por você.'}

    if self.normal_user:
        punter_payed =  str(self.normal_user.pk) +' - '+ str(self.normal_user.first_name)
    elif self.user:
        punter_payed = str(self.user.pk) +' - '+ str(self.user.first_name)

    self.reward.reward_date = tzlocal.now()
    self.reward.who_rewarded = Seller.objects.get(pk=user.pk)
    self.reward.save()

    PunterPayedHistory.objects.create(punter_payed=punter_payed,
        seller=user.seller,
        ticket_winner=self,
        payed_value=self.reward.real_value,
        store=self.store)

    return {'success':True,
            'message':'O Apostador ' + punter_payed  + ' foi marcado como Pago'}

def cotation_sum(self):
    from core.models import CotationCopy

    valid_cotations = CotationCopy.objects\
    .filter(ticket=self, game__game_status__in = (0,1,3))\
    .exclude(original_cotation__settlement=-1)
    
    cotation_sum = 1
    for cotation in valid_cotations:
        cotation_sum *= cotation.price
    if cotation_sum == 1:
        return 0

    from utils.models import GeneralConfigurations
    try:
        general_config = GeneralConfigurations.objects.get(pk=1)
        max_cotation_sum = general_config.max_cotation_sum
    except GeneralConfigurations.DoesNotExist:
        max_cotation_sum = 100000
    
    if cotation_sum > max_cotation_sum:
        cotation_sum = max_cotation_sum

    return round(cotation_sum,2)

