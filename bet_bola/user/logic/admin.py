
def manage_user_credit(self, user, value):
    from history.models import CreditTransactions      
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
        CreditTransactions.objects.create(creditor=self,
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
    self.user_permissions.add(be_admin_perm)