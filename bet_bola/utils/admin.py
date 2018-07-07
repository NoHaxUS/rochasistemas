from django.contrib import admin
from .models import Overview, MarketReduction
from django.contrib import messages


@admin.register(Overview)
class OverviewAdmin(admin.ModelAdmin):
    list_display = ('pk','total_revenue','total_out_money','seller_out_money','manager_out_money','total_net_value')
 
@admin.register(MarketReduction)
class MarketReductionsAdmin(admin.ModelAdmin):
    pass