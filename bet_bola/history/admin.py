from django.contrib import admin
from user.models import CustomUser
from .models import SellerSalesHistory,ManagerTransactions,RevenueHistorySeller,RevenueHistoryManager, PunterPayedHistory
from user.models import CustomUser
from django.utils.translation import gettext_lazy as _


@admin.register(SellerSalesHistory)
class SellerSalesHistoryAdmin(admin.ModelAdmin):
	search_fields = ['seller__first_name']
	list_display = ('pk','seller','bet_ticket','sell_date','value','seller_before_balance','seller_after_balance')
	list_display_links = ('pk','seller')


@admin.register(ManagerTransactions)
class ManagerTransactionsAdmin(admin.ModelAdmin):
	search_fields = ['manager__first_name']
	list_display = ('pk','manager','seller','transaction_date','transferred_amount','seller_before_balance','seller_after_balance')
	list_display_links = ('pk','manager')


@admin.register(RevenueHistorySeller)
class RevenueHistorySellerAdmin(admin.ModelAdmin):
	search_fields = ['seller__first_name']
	list_display = ('pk','who_reseted_revenue','seller','revenue_reseted_date','final_revenue','actual_comission','earned_value')
	list_display_links = ('pk','seller')


@admin.register(RevenueHistoryManager)
class RevenueHistoryManagerAdmin(admin.ModelAdmin):
	search_fields = ['manager__first_name']
	list_display = ('pk','who_reseted_revenue','manager','revenue_reseted_date','final_revenue','actual_comission','earned_value')
	list_display_links = ('pk','manager')



@admin.register(PunterPayedHistory)
class PunterPayedHistoryAdmin(admin.ModelAdmin):
	search_fields = ['seller__first_name', 'ticket_winner__pk']
	list_display = ('pk','punter_payed','seller','ticket_winner','payment_date','payed_value')
	list_display_links = ('pk','punter_payed')