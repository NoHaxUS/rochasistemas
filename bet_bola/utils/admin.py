from django.contrib import admin
from .models import Overview, MarketReduction, Comission
from django.contrib import messages



@admin.register(Comission)
class ComissionAdmin(admin.ModelAdmin):
    search_fields = ['seller_related__id','seller_related__username', 'seller_related__first_name']
    list_display = ('seller_related','simple','double','triple_amount', 'four_plus_amount','total_simple','total_double','total_triple','total_plus', 'total_comission')
    list_editable = ('simple', 'double','triple_amount','four_plus_amount')
    actions = None

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.has_perm('user.be_manager'):
            return qs.filter(seller_related__my_manager=request.user.manager)
        if request.user.has_perm('user.be_seller'):
            return qs.filter(seller_related__id=request.user.pk)

@admin.register(Overview)
class OverviewAdmin(admin.ModelAdmin):
    list_display = ('pk','total_revenue','total_out_money','seller_out_money','manager_out_money','total_net_value')
 

@admin.register(MarketReduction)
class MarketReductionsAdmin(admin.ModelAdmin):
    list_display = ('market_to_reduct','reduction_percentual')