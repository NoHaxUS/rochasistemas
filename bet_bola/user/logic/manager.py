def reset_revenue(self, who_reseted_revenue):
    from core.models import Payment
    from user.models import Seller
    from history.models import RevenueHistoryManager, WinnerPaymentHistory

    RevenueHistoryManager.objects.create(who_reseted_revenue=who_reseted_revenue,
    manager=self,
    final_revenue=self.actual_revenue(),
    actual_comission=self.commission,
    earned_value=self.net_value(),
    final_out_value=self.out_money(),
    profit = self.actual_revenue() - self.out_money())

    sellers = Seller.objects.filter(my_manager=self)
    for seller in sellers:
        payments_not_rewarded = Payment.objects.filter(who_set_payment=seller)            
        payeds_open = WinnerPaymentHistory.objects.filter(seller=seller, is_closed_for_manager=False)
        payeds_open.update(is_closed_for_manager=True)


def out_money(self):
    from history.models import WinnerPaymentHistory
    from user.models import Seller

    sellers = Seller.objects.filter(my_manager=self)

    payed_sum = 0
    for seller in sellers:
        payeds_open = WinnerPaymentHistory.objects.filter(seller=seller, is_closed_for_manager=False)

        for payed in payeds_open:
            payed_sum += payed.payed_value

    return payed_sum

def get_commission(self):
    return str(round(self.commission,0)) + "%"    

def net_value(self):
    from core.models import Seller
    sellers = Seller.objects.filter(my_manager=self)


    if self.based_on_profit:
        total_net_value = self.net_value_before_comission() * (self.commission / 100)
        return round(total_net_value, 2)
    else:
        total_net_value = self.actual_revenue() * (self.commission / 100)
        return round(total_net_value, 2)        


def real_net_value(self):
    return self.net_value_before_comission() - self.net_value()    


def net_value_before_comission(self):
    return self.actual_revenue() - self.out_money()    

def actual_revenue(self):
    from core.models import Seller
    from core.models import Ticket

    sellers = Seller.objects.filter(my_manager=self)

    total_revenue = 0
    for seller in sellers:
        tickets_not_rewarded = Ticket.objects.filter(payment__who_set_payment=seller).exclude(payment__status='Cancelado')
        for ticket in tickets_not_rewarded:
            total_revenue += ticket.value
    return total_revenue

def manage_credit(self, obj, is_new=False):
    from history.models import ManagerTransactions
    from core.models import Seller

    seller = Seller.objects.get(pk=obj.pk)
    manager_before_balance = self.credit_limit_to_add

    if not self.can_sell_unlimited:
        if is_new:
            seller_before_balance = 0
            diff = obj.credit_limit
            seller_after_balance = obj.credit_limit
        else:
            seller_before_balance = seller.credit_limit
            diff = obj.credit_limit - seller.credit_limit
            seller_after_balance = seller.credit_limit + diff

        manager_balance_after = self.credit_limit_to_add - diff


        if manager_balance_after < 0:
            if is_new:
                return {'success': False,
                'message': 'Você não tem saldo suficiente para adicionar crédito, porém o cambista foi criado.'}
            else:
                return {'success': False,
                'message': 'Você não tem saldo suficiente.'}
        
        elif obj.credit_limit < 0:
            return {'success': False,
            'message': 'O cambista não pode ter saldo negativo.'}
        else:
            self.credit_limit_to_add -= diff
            self.save()

            if is_new:
                seller.credit_limit = obj.credit_limit
                seller.save()
    else:
        if obj.credit_limit < 0:
            return {'success': False,
                'message': 'O cambista não pode ter saldo negativo.'}

        manager_balance_after = 0

        seller_before_balance = seller.credit_limit
        diff = obj.credit_limit - seller.credit_limit
        seller_after_balance = seller.credit_limit + diff

        self.save()

    if not self.can_sell_unlimited:
        if not manager_before_balance == manager_balance_after:
            ManagerTransactions.objects.create(manager=self,
            seller=seller,
            transferred_amount=diff,
            manager_before_balance=manager_before_balance,
            manager_after_balance=manager_balance_after,
            seller_before_balance=seller_before_balance,
            seller_after_balance=seller_after_balance,
            store=self.my_store)
    else:
        ManagerTransactions.objects.create(manager=self,
        seller=seller,
        transferred_amount=diff,
        manager_before_balance=manager_before_balance,
        manager_after_balance=manager_balance_after,
        seller_before_balance=seller_before_balance,
        seller_after_balance=seller_after_balance,
        store=self.my_store)

    return {'success': True,
        'message': 'Transação realizada.'}

def define_default_permissions(self):
    from django.contrib.auth.models import Permission

    be_manager_perm = Permission.objects.get(codename='be_manager')
    view_managertransactions_perm = Permission.objects.get(codename='view_managertransactions')
    view_revenuehistoryseller_perm = Permission.objects.get(codename='view_revenuehistoryseller')
    view_sellersaleshistory_perm = Permission.objects.get(codename='view_sellersaleshistory')
    view_punterpayedhistory_perm = Permission.objects.get(codename='view_punterpayedhistory')
    view_revenuehistorymanager = Permission.objects.get(codename='view_revenuehistorymanager')
    change_seller = Permission.objects.get(codename='change_seller')
    add_seller = Permission.objects.get(codename='add_seller')
    view_manager = Permission.objects.get(codename='view_manager')
    view_ticket_perm = Permission.objects.get(codename='view_ticket')
    view_punter_perm = Permission.objects.get(codename='view_punter')
    change_ticket_perm = Permission.objects.get(codename='change_ticket')
    view_ticketcancelationhistory = Permission.objects.get(codename='view_ticketcancelationhistory')
    view_comission = Permission.objects.get(codename='view_comission')
    
    self.user_permissions.add(be_manager_perm,view_managertransactions_perm,
    view_revenuehistoryseller_perm,view_sellersaleshistory_perm,
    view_punterpayedhistory_perm, view_revenuehistorymanager, change_seller, add_seller,
    view_manager, view_ticket_perm, view_punter_perm, change_ticket_perm, 
    view_ticketcancelationhistory, view_comission)