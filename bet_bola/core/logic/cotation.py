def get_store_price(self, store):
    from utils.models import GeneralConfigurations
    from core.models import CotationModified

    config = store.my_configuration
    
    if self.price > config.max_cotation_value:
        self.price = config.max_cotation_value					
    if CotationModified.objects.filter(cotation=self, store=store, price__gt=1).exists():					
        self.price = CotationModified.objects.filter(cotation=self, store=store).first().price
    elif self.market.my_modification.filter(store=store).exclude(reduction_percentual=100):							
        self.price = self.price * self.market.my_modification.get(store=store).reduction_percentual / 100										
    else:					
        self.price = self.price * config.cotations_percentage / 100													
    
    if self.price < 1:
        self.price = 1.01

    return self.price
