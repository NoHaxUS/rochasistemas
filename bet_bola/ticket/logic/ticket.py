from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
import utils.timezone as tzlocal
  

def hide_ticket(self):
    self.available = False
    self.save()
    return True

def show_ticket(self):
    self.available = True
    self.save()
    return True
  

def cancel_ticket(self, who_canceling):

    if not who_canceling.is_superuser and not who_canceling.has_perm('user.be_seller'):
        return {
            'success': False,
            'message': 'Esse Usuário não tem permissão para cancelar Bilhetes.'
        }
    
    if not self.status == 0:
        return {
            'success': False,
            'message': 'Não é possível cancelar esse Bilhete '+ str(self.pk) + ' pois o mesmo não está em aberto.'
        }
    
    if not self.payment.status == 2:
        return {
            'success': False,
            'message': 'O Bilhete '+ str(self.pk) +' não foi Pago para ser cancelado.'
        }

    if not who_canceling.is_superuser:
        if self.payment.date + timezone.timedelta(minutes=int(who_canceling.seller.limit_time_to_cancel)) < tzlocal.now():
            return {
                'success':False,
                'message':' Tempo limite para cancelar o Bilhete '+ str(self.pk) +' foi excedido.'
            }
        
        if not who_canceling == self.payment.who_paid:
            return {
                'success':False,
                'message':'Você não pode cancelar um Bilhete que você não Pagou.'
            }
    
    
    who_paid = self.payment.who_paid
    if not who_paid.can_sell_unlimited:
        who_paid.credit_limit += self.value
        who_paid.save()

    self.status = 5
    self.save()

    from history.models import TicketCancelationHistory

    TicketCancelationHistory.objects.create(
        who_canceling=who_canceling,
        ticket=self,
        date=tzlocal.now(),
        who_paid=who_paid,
        store=self.store
    )

    return {
        'success':True,
        'message':'O Bilhete '+ str(self.pk) +' foi cancelado.'
    }

def validate_ticket(self, who_validating):         
    
    if not who_validating.is_superuser and not who_validating.has_perm('user.be_seller'):
        return {
            'success': False,
            'message': 'Esse Usuário não tem permissão para validar Bilhetes.'
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
            'message':'O Bilhete '+ str(self.pk) +' não está Aguardando Pagamento.'
        }

    if not self.status == 0:
        return {
            'success': False,
            'message': 'Não é possível validar esse Bilhete ' + str(self.pk) + ' pois o mesmo não está em aberto.'
        }

    for cotation in self.cotations.all():
        if cotation.game.start_date < tzlocal.now():
            return {
                'success': False,
                'message':'O Bilhete '+ str(self.pk) +' não pode ser pago, pois contém cotas de jogo(s) que já iniciaram.'
            }
    
    seller_before_balance = 0
    seller_after_balance= 0

    if not who_validating.is_superuser:
        if not who_validating.seller.can_sell_unlimited:
            if self.value > who_validating.seller.credit_limit:                
                return {
                'success':False,
                'message':'Você não tem créditos para pagar esse Bilhete: ' + str(self.pk)
            }

            seller_before_balance = who_validating.seller.credit_limit
            who_validating.seller.credit_limit -= self.value
            seller_after_balance = who_validating.seller.credit_limit
            who_validating.seller.save()
                
    self.save()
    self.payment.status = 2
    self.payment.date = tzlocal.now()
    self.payment.who_paid = who_validating
    self.payment.save()

    from history.models import TicketValidationHistory

    TicketValidationHistory.objects.create(
        who_validated=who_validating,
        ticket=self,
        bet_value=self.bet_value,
        date=tzlocal.now(),
        balance_before=seller_before_balance,
        balance_after=seller_after_balance,
        store=self.store
    )
    
    return {
        'success':True,
        'message':'Bilhete '+ str(self.pk) +' PAGO com Sucesso.'
    }


def reward_winner(self, who_rewarding_the_winner):

    if not who_rewarding_the_winner.is_superuser and not who_rewarding_the_winner.has_perm('user.be_seller'):
        return {
            'success': False,
            'message': 'Esse Usuário não tem permissão para Pagar Ganhadores.'
        }

    if not self.status == 4:   
        return {
            'success':False,
            'message':'Esse bilhete (' +str(self.pk) +') não está apto a prestação de contas.'    
        }

    if not self.payment.who_paid == who_rewarding_the_winner:
        return {
            'success':False,
            'message':'Você só pode recompensar ganhadores de apostas pagas por você.'
        }

    self.status = 2
    self.save()
    self.reward.date = tzlocal.now()
    self.reward.who_rewarded_the_winner = who_rewarding_the_winner
    self.reward.save()

    from history.models import WinnerPaymentHistory
    WinnerPaymentHistory.objects.create(
        winner_name=self.owner.first_name,
        who_rewarded_the_winner=who_rewarding_the_winner,
        ticket=self,
        date=tzlocal.now(),
        bet_value=self.reward.real_value,
        store=self.store
    )

    return {
        'success':True,
        'message':'O Ganhador ' + self.owner.first_name  + ' foi Pago.'
    }


def cotation_sum(self):
    from core.models import CotationCopy

    valid_cotations = CotationCopy.objects.filter(ticket=self, original_cotation__game__status__in = (0,1,3))
    
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
        max_cotation_sum = 1000000
    
    if cotation_sum > max_cotation_sum:
        cotation_sum = max_cotation_sum

    return round(cotation_sum, 2)
