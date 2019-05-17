from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
import utils.timezone as tzlocal
  

def hide_ticket(self):
    self.visible = False
    self.save()
    return True

def show_ticket(self):
    self.visible = True
    self.save()
    return True
  

def cancel_ticket(self, who_canceling):

    if not who_canceling.is_superuser and not who_canceling.has_perm('user.be_seller'):
        return {
            'success': False,
            'message': 'Esse Usuário não tem permissão para cancelar Tickets.'
        }
    
    if not self.status == 0:
        return {
            'success': False,
            'message': 'Não é possível cancelar esse Ticket '+ str(self.pk) + ' pois o mesmo não está em aberto.'
        }
    
    if not self.payment.status == 2:
        return {
            'success': False,
            'message': 'O Ticket '+ str(self.pk) +' não foi Pago para ser cancelado.'
        }

    if not who_canceling.is_superuser:
        if self.payment.date + timezone.timedelta(minutes=int(who_canceling.seller.limit_time_to_cancel)) < tzlocal.now():
            return {
                'success':False,
                'message':' Tempo limite para cancelar o Ticket '+ str(self.pk) +' foi excedido.'
            }
        
        if not who_canceling == self.payment.who_paid:
            return {
                'success':False,
                'message':'Você não pode cancelar um Ticket que você não Pagou.'
            }
    
    
    who_paid = self.payment.who_paid
    if not who_paid.can_sell_unlimited:
        who_paid.credit_limit += self.value
        who_paid.save()

    self.payment.status = 5
    self.payment.date = None
    self.payment.save()
    self.save()

    from history.models import TicketCancelationHistory

    TicketCancelationHistory.objects.create(
        who_canceling=str(who_canceling.pk) + ' - ' + who_canceling.username,
        ticket_cancelled=self,
        cancelation_date=tzlocal.now(),
        who_paid=who_paid,
        store=self.store
    )

    return {
        'success':True,
        'message':'O Ticket '+ str(self.pk) +' foi cancelado.'
    }

def validate_ticket(self, who_validating):         
    
    if not who_validating.is_superuser and not who_validating.has_perm('user.be_seller'):
        return {
            'success': False,
            'message': 'Esse Usuário não tem permissão para validar Tickets.'
        }

    if self.reward.value >= self.store.config.alert_bet_value:
        if self.store.email:
            subject = 'Alerta de aposta'
            message = 'Uma aposta com recompensa no valor de R$' + self.reward.value + ' foi efetuada em sua plataforma.'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [self.store.email,]
            send_mail( subject, message, email_from, recipient_list )
    
    if not self.payment.status == 0:
        return {
            'success':False,
            'message':'O Ticket '+ str(self.pk) +' não está Aguardando Pagamento.'
        }

    if not self.status == 0:
        return {
            'success': False,
            'message': 'Não é possível validar esse Ticket ' + str(self.pk) + ' pois o mesmo não está em aberto.'
        }

    for cotation in self.cotations.all():
        if cotation.game.start_date < tzlocal.now():
            return {
                'success': False,
                'message':'O Ticket '+ str(self.pk) +' não pode ser pago, pois contém cotas de jogo(s) que já iniciaram.'
            }

    if not who_validating.is_superuser:
        seller_before_balance = 0
        seller_after_balance= 0

        if not who_validating.seller.can_sell_unlimited:
            if self.value > who_validating.seller.credit_limit:                
                return {
                'success':False,
                'message':'Você não tem saldo suficiente para pagar o Ticket: ' + str(self.pk)
            }

            seller_before_balance = who_validating.seller.credit_limit
            who_validating.seller.credit_limit -= self.value
            seller_after_balance = who_validating.seller.credit_limit
            who_validating.seller.save()
                
    self.save()
    self.payment.status = 2
    self.payment.date = tzlocal.now()
    self.payment.who_paid = who_validating

    if who_validating.is_superuser:
        self.payment.who_paid_type = 1
    else:
        self.payment.who_paid_type = 0
    
    self.payment.save()

    from history.models import TicketValidationHistory

    TicketValidationHistory.objects.create(
        who_validating=str(who_validating.pk + ' - ' + who_validating.username),
        ticket=self,
        bet_value=self.bet_value,
        balance_before=seller_before_balance,
        balance_after=seller_after_balance,
        store=self.store
    )
    
    return {
        'success':True,
        'message':'Bilhete '+ str(self.pk) +' PAGO com Sucesso.'
    }


def pay_winner(self, who_paying_winner):
    from history.models import WinnerPaymentHistory
    from user.models import Seller
    from ticket.models import Ticket, Payment

    if not who_paying_winner.is_superuser and not who_paying_winner.has_perm('user.be_seller'):
        return {
            'success': False,
            'message': 'Esse Usuário não tem permissão para Pagar Ganhadores.'
        }

    if not self.status == 4:   
        return {
            'success':False,
            'message':'Esse bilhete (' +str(self.pk) +') não está apto a prestação de contas.'    
        }

    if not self.payment.who_paid == who_paying_winner:
        return {
            'success':False,
            'message':'Você só pode recompensar ganhadores de apostas pagas por você.'
        }

    self.reward.date = tzlocal.now()
    self.reward.who_rewarded_the_winner = who_paying_winner
    if who_paying_winner.is_superuser:
        self.reward.who_rewarded_type = 1
    else:
        self.reward.who_rewarded_type = 0
    self.reward.save()

    WinnerPaymentHistory.objects.create(
        winner_payed=self.owner.first_name,
        seller=who_paying_winner.seller,
        ticket_winner=self,
        payed_value=self.reward.real_value,
        store=self.store
    )

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

