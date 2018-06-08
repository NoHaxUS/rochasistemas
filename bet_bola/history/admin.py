from django.contrib import admin
from user.models import CustomUser
from .models import SellerSalesHistory,ManagerTransactions,RevenueHistorySeller,RevenueHistoryManager
from user.models import CustomUser
from django.utils.translation import gettext_lazy as _


@admin.register(SellerSalesHistory)
class SellerSalesHistoryAdmin(admin.ModelAdmin):
	search_fields = ['seller__first_name']
	#fields = ('name','ht_score','ft_score','status_game',)
	list_display = ('seller',)
	#list_display_links = ('pk','seller','bet_ticket')