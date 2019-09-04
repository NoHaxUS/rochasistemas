def get_store_price(self, store):
    from utils.models import GeneralConfigurations
    from core.models import CotationModified
    from decimal import Decimal

    config = store.my_configuration
    cotation_modified = CotationModified.objects.filter(cotation=self, store=store, price__gt=1)
    market_reducation = self.market.my_modifications.filter(store=store, modification_available=True)    
    price = self.price    
        
    if cotation_modified:
        price = cotation_modified.first().price    
    elif market_reducation:						        	        
        price = price * market_reducation.first().reduction_percentual / 100										
    else:        
        price = price * config.cotations_percentage / 100													
    
    if price > config.max_cotation_value:
        price = config.max_cotation_value
        
    if price < 1:
        price = 1.01
    
    return Decimal(str(price))
