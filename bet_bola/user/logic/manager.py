
def manage_credit(self, obj, is_new=False):
    from history.models import ManagerTransactions
    from core.models import Seller

    seller = Seller.objects.get(pk=obj.pk)
    manager_before_balance = self.credit_limit

    if not self.can_sell_unlimited:
        if is_new:
            seller_before_balance = 0
            diff = obj.credit_limit
            seller_after_balance = obj.credit_limit
        else:
            seller_before_balance = seller.credit_limit
            diff = obj.credit_limit - seller.credit_limit
            seller_after_balance = seller.credit_limit + diff

        manager_balance_after = self.credit_limit - diff


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
            self.credit_limit -= diff
            self.save()

            if is_new:
                print(seller.credit_limit)
                seller.credit_limit = obj.credit_limit
                seller.save()
                print(seller.credit_limit)
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
    self.user_permissions.add(be_manager_perm)
    