
def manage_seller_credit(self, seller, value):
    from history.models import ManagerTransactions
    from core.models import Seller
    
    manager_before_balance = self.credit_limit    
    if self.can_sell_unlimited or self.credit_limit - value >= 0:
        seller_before_balance = seller.credit_limit        
        seller.credit_limit += value
        seller_after_balance =  seller.credit_limit

        if not self.can_sell_unlimited:
            self.credit_limit -= value

        manager_balance_after = self.credit_limit            
        
        if seller.credit_limit < 0:
            return {'success': False,
            'message': 'O cambista não pode ter saldo negativo.'}
        else:                        
            self.save()                        
            seller.save()            
            ManagerTransactions.objects.create(creditor=self,
            user=seller,
            transferred_amount=value,
            creditor_before_balance=manager_before_balance,
            creditor_after_balance=manager_balance_after,
            user_before_balance=seller_before_balance,
            user_after_balance=seller_after_balance,
            store=self.my_store)

            return {'success': True,
                'message': 'Transação realizada com sucesso.'}
    else:        
        return {'success': False,
            'message': 'Você não tem saldo suficiente para executar essa operação.'}


def define_default_permissions(self):
    from django.contrib.auth.models import Permission

    be_manager_perm = Permission.objects.get(codename='be_manager')
    self.user_permissions.add(be_manager_perm)
    