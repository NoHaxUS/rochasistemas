def get_store_price(self, store):
    from utils.models import GeneralConfigurations
    from core.models import CotationModified

    config = store.my_configuration
    cotation_modified = CotationModified.objects.filter(cotation=self, store=store, price__gt=1)
    market_reducation = self.market.my_modifications.filter(store=store).exclude(reduction_percentual=100)
    
    
    if self.price > config.max_cotation_value:
        self.price = config.max_cotation_value
    
    if cotation_modified:
        self.price = cotation_modified.first().price
    
    elif market_reducation:							
        self.price = self.price * market_reducation.first().reduction_percentual / 100										
    else:
        self.price = self.price * config.cotations_percentage / 100													
    
    if self.price < 1:
        self.price = 1.01

    return self.price
