def get_store_price(self, store):
    from utils.models import GeneralConfigurations
    from core.models import CotationModified
    from decimal import Decimal

    config = store.my_configuration
    cotation_modified = CotationModified.objects.filter(cotation=self, store=store, price__gt=1)
    market_reducation = self.market.my_modifications.filter(store=store).exclude(reduction_percentual=100)    
    price = 0
    if self.price > config.max_cotation_value:
        price = config.max_cotation_value
    
    if cotation_modified:
        price = cotation_modified.first().price
    
    elif market_reducation:							
        price = self.price * market_reducation.first().reduction_percentual / 100										
    else:
        price = self.price * config.cotations_percentage / 100													
    
    if self.price < 1:
        price = 1.01
    
    return Decimal(str(price))
