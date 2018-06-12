from django.contrib import admin
from user.models import CustomUser
from .models import SellerSalesHistory,ManagerTransactions,RevenueHistorySeller,RevenueHistoryManager, PunterPayedHistory
from user.models import CustomUser
from django.utils.translation import gettext_lazy as _
from admin_view_permission.admin import AdminViewPermissionModelAdmin


@admin.register(SellerSalesHistory)
class SellerSalesHistoryAdmin(admin.ModelAdmin):
	search_fields = ['seller__first_name']
	list_display = ('pk','seller','bet_ticket','sell_date','value','seller_before_balance','seller_after_balance')
	list_display_links = ('pk','seller')

	def get_queryset(self, request):
		qs = super().get_queryset(request)
		if request.user.is_superuser:
			return qs
		elif request.user.has_perm('user.be_seller'):
			return SellerSalesHistory.objects.filter(seller=request.user.seller)
		
		elif request.user.has_perm('user.be_manager'):
			return SellerSalesHistory.objects.filter(seller__my_manager=request.user.manager)
		
		return qs



@admin.register(ManagerTransactions)
class ManagerTransactionsAdmin(AdminViewPermissionModelAdmin):
	search_fields = ['manager__first_name']
	list_display = ('pk','manager','seller','transaction_date','transferred_amount','manager_before_balance','manager_after_balance','seller_before_balance','seller_after_balance')
	list_display_links = ('pk','manager')


	def get_queryset(self, request):
		qs = super().get_queryset(request)
		if request.user.is_superuser:
			return qs
		elif request.user.has_perm('user.be_seller'):
			return ManagerTransactions.objects.filter(seller=request.user.seller)

		elif request.user.has_perm('user.be_manager'):
			return ManagerTransactions.objects.filter(manager=request.user.manager)
		
		return qs


@admin.register(RevenueHistorySeller)
class RevenueHistorySellerAdmin(AdminViewPermissionModelAdmin):
	search_fields = ['seller__first_name']
	list_display = ('pk','who_reseted_revenue','seller','revenue_reseted_date','final_revenue','actual_comission','earned_value')
	list_display_links = ('pk','seller')


	def get_queryset(self, request):
		qs = super().get_queryset(request)
		if request.user.is_superuser:
			return qs
		elif request.user.has_perm('user.be_seller'):
			return RevenueHistorySeller.objects.filter(seller=request.user.seller)

		elif request.user.has_perm('user.be_manager'):
			return RevenueHistorySeller.objects.filter(seller__my_manager=request.user.manager)
		
		return qs


@admin.register(RevenueHistoryManager)
class RevenueHistoryManagerAdmin(admin.ModelAdmin):
	search_fields = ['manager__first_name']
	list_display = ('pk','who_reseted_revenue','manager','revenue_reseted_date','final_revenue','actual_comission','earned_value')
	list_display_links = ('pk','manager')


	def get_queryset(self, request):
		qs = super().get_queryset(request)
		if request.user.is_superuser:
			return qs

		elif request.user.has_perm('user.be_manager'):
			return RevenueHistoryManager.objects.filter(manager=request.user.manager)
		
		return qs



@admin.register(PunterPayedHistory)
class PunterPayedHistoryAdmin(AdminViewPermissionModelAdmin):
	search_fields = ['punter_payed','seller__first_name', 'ticket_winner__id']
	list_display = ('pk','punter_payed','seller','ticket_winner','payment_date','payed_value')
	list_display_links = ('pk','punter_payed')


	def get_queryset(self, request):
		qs = super().get_queryset(request)
		if request.user.is_superuser:
			return qs
		elif request.user.has_perm('user.be_seller'):
			return PunterPayedHistory.objects.filter(seller=request.user.seller)

		elif request.user.has_perm('user.be_manager'):
			return PunterPayedHistory.objects.filter(seller__my_manager=request.user.manager)
		
		return qs

