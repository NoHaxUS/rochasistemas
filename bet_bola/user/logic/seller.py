def reset_revenue(self, who_reseted_revenue):
    from ticket.models import Payment
    from history.models import RevenueHistorySeller, WinnerPaymentHistory

    RevenueHistorySeller.objects.create(who_reseted_revenue=who_reseted_revenue,
    seller=self,
    final_revenue=self.actual_revenue(),
    earned_value=self.net_value(),
    final_out_value=self.out_money(),
    profit = self.actual_revenue() - self.out_money(),
    store=self.my_store)

    payeds_open = WinnerPaymentHistory.objects.filter(seller=self, is_closed_for_seller=False)
    payeds_open.update(is_closed_for_seller=True)


def full_name(self):
    return self.first_name + ' ' + self.last_name    

def net_value(self):        
    total_net_value = self.comissions.total_comission(None,None)
    return round(total_net_value, 2)    

def real_net_value(self):
    return self.actual_revenue() -  (self.net_value() + self.out_money())

def see_comissions(self):
    from django.utils.html import format_html
    return format_html(
        '<a href="/admin/utils/comission/?q={}">Ver Comissões</a>',
        self.username,
    )    

def get_commission(self):
    return str(round(self.commission,0)) + "%"

def out_money(self):
    from history.models import WinnerPaymentHistory

    payed_sum = 0
    payeds_open = WinnerPaymentHistory.objects.filter(seller=self, is_closed_for_seller=False)

    for payed in payeds_open:
        payed_sum += payed.payed_value
    return payed_sum

def actual_revenue(self):

    from core.models import Ticket
    
    total_revenue = 0
    # tickets_not_rewarded = Ticket.objects.filter(payment__who_set_payment=self,
    # payment__seller_was_rewarded=False).exclude(payment__status='Cancelado')
    tickets_not_rewarded = Ticket.objects.filter(payment__who_paid=self
    ).exclude(payment__status='Cancelado')
    for ticket in tickets_not_rewarded:
        total_revenue += ticket.value

    return total_revenue

def save(self, *args, **kwargs):
    self.clean()
    if not self.password.startswith('pbkdf2'):			
        self.set_password(self.password)
    self.is_superuser = False
    self.is_staff = True
    super().save()

    from utils.models import Comission
    comission = Comission.objects.filter(seller_related=self)
    if not comission:
        Comission(seller_related=self,store=self.my_store).save()
    self.define_default_permissions()

def define_default_permissions(self):        
    from django.contrib.auth.models import Permission
    
    be_seller_perm = Permission.objects.get(codename='be_seller')
    change_ticket_perm = Permission.objects.get(codename='change_ticket')
    view_managertransactions_perm = Permission.objects.get(codename='view_managertransactions')
    view_revenuehistoryseller_perm = Permission.objects.get(codename='view_revenuehistoryseller')
    view_sellersaleshistory_perm = Permission.objects.get(codename='view_sellersaleshistory')
    view_punterpayedhistory_perm = Permission.objects.get(codename='view_punterpayedhistory')
    view_seller_perm = Permission.objects.get(codename='view_seller')
    view_punter_perm = Permission.objects.get(codename='view_punter')
    view_ticketcancelationhistory = Permission.objects.get(codename='view_ticketcancelationhistory')
    view_comission = Permission.objects.get(codename='view_comission')
    
    self.user_permissions.add(be_seller_perm, change_ticket_perm, 
    view_managertransactions_perm, view_revenuehistoryseller_perm, 
    view_sellersaleshistory_perm, view_punterpayedhistory_perm,
    view_seller_perm, view_punter_perm, view_ticketcancelationhistory, 
    view_comission)