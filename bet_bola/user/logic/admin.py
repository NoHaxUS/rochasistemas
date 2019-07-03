
def manage_user_credit(self, user, value):
    from history.models import ManagerTransactions      
    if user.user_type == 3:
        user = user.manager
    elif user.user_type == 2:
        user = user.seller

    user_before_balance = user.credit_limit        
    user.credit_limit += value
    user_after_balance =  user.credit_limit        
    
    if user.credit_limit < 0:
        return {'success': False,
        'message': 'O cambista não pode ter saldo negativo.'}
    else:                        
        self.save()                        
        user.save()            
        ManagerTransactions.objects.create(creditor=self,
        user=user,
        transferred_amount=value,
        creditor_before_balance=0,
        creditor_after_balance=0,
        user_before_balance=user_before_balance,
        user_after_balance=user_after_balance,
        store=self.my_store)

        return {'success': True,
            'message': 'Transação realizada com sucesso.'}
    
def define_default_permissions(self):
    from django.contrib.auth.models import Permission
    
    be_admin_perm = Permission.objects.get(codename='be_admin')
    # view_managertransactions_perm = Permission.objects.get(codename='view_managertransactions')
    # view_revenuehistoryuser_perm = Permission.objects.get(codename='view_revenuehistoryuser')
    # view_usersaleshistory_perm = Permission.objects.get(codename='view_usersaleshistory')
    # view_punterpayedhistory_perm = Permission.objects.get(codename='view_punterpayedhistory')
    # view_revenuehistorymanager = Permission.objects.get(codename='view_revenuehistorymanager')
    # change_user = Permission.objects.get(codename='change_user')
    # add_user = Permission.objects.get(codename='add_user')
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
    # view_revenuehistoryuser_perm,view_usersaleshistory_perm,
    # view_punterpayedhistory_perm, view_revenuehistorymanager, change_user, add_user,
    # view_manager, add_manager, change_manager, view_ticket_perm, view_punter_perm, change_ticket_perm, 
    # view_ticketcancelationhistory, view_comission)
