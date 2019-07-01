
def manage_seller_credit(self, seller, value):
    from history.models import ManagerTransactions
    from core.models import Seller        
    
    seller_before_balance = seller.credit_limit        
    seller.credit_limit += value
    seller_after_balance =  seller.credit_limit        
    
    if seller.credit_limit < 0:
        return {'success': False,
        'message': 'O cambista não pode ter saldo negativo.'}
    else:                        
        self.save()                        
        seller.save()            
        ManagerTransactions.objects.create(creditor=self,
        seller=seller,
        transferred_amount=value,
        creditor_before_balance=0,
        creditor_after_balance=0,
        seller_before_balance=seller_before_balance,
        seller_after_balance=seller_after_balance,
        store=self.my_store)

        return {'success': True,
            'message': 'Transação realizada com sucesso.'}
    
def define_default_permissions(self):
    from django.contrib.auth.models import Permission
    
    be_admin_perm = Permission.objects.get(codename='be_admin')
    # view_managertransactions_perm = Permission.objects.get(codename='view_managertransactions')
    # view_revenuehistoryseller_perm = Permission.objects.get(codename='view_revenuehistoryseller')
    # view_sellersaleshistory_perm = Permission.objects.get(codename='view_sellersaleshistory')
    # view_punterpayedhistory_perm = Permission.objects.get(codename='view_punterpayedhistory')
    # view_revenuehistorymanager = Permission.objects.get(codename='view_revenuehistorymanager')
    # change_seller = Permission.objects.get(codename='change_seller')
    # add_seller = Permission.objects.get(codename='add_seller')
    # view_manager = Permission.objects.get(codename='view_manager')
    # add_manager = Permission.objects.get(codename='add_manager')
    # change_manager = Permission.objects.get(codename='change_manager')
    # view_ticket_perm = Permission.objects.get(codename='view_ticket')
    # view_punter_perm = Permission.objects.get(codename='view_punter')
    # change_ticket_perm = Permission.objects.get(codename='change_ticket')
    # view_ticketcancelationhistory = Permission.objects.get(codename='view_ticketcancelationhistory')
    # view_comission = Permission.objects.get(codename='view_comission')
    
    self.user_permissions.add(be_admin_perm)
    #view_managertransactions_perm,
    # view_revenuehistoryseller_perm,view_sellersaleshistory_perm,
    # view_punterpayedhistory_perm, view_revenuehistorymanager, change_seller, add_seller,
    # view_manager, add_manager, change_manager, view_ticket_perm, view_punter_perm, change_ticket_perm, 
    # view_ticketcancelationhistory, view_comission)
