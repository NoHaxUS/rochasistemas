from django.db.models.query import QuerySet
from django.db.models import Q
from django.db.models import Count
from django.utils import timezone
import datetime


class GamesQuerySet(QuerySet):


	def able_games(self):
		return self.annotate(cotations_count=Count('cotations')).filter(cotations_count__gt=0).filter(status_game="NS").filter(start_game_date__gte=timezone.now())

	def today_able_games(self):
		return self.annotate(cotations_count=Count('cotations')).filter(cotations_count__gt=0).filter(status_game="NS").filter(start_game_date__gte=timezone.now()).filter(start_game_date__lte=(timezone.now() + timezone.timedelta(days=1)) )

	def tomorrow_able_games(self):
		return self.annotate(cotations_count=Count('cotations')).filter(cotations_count__gt=0).filter(status_game="NS").filter(start_game_date__date=timezone.now().date() + timezone.timedelta(days=1) )

GamesManager = GamesQuerySet.as_manager


class CotationsQuerySet(QuerySet):

	def standard_cotations(self):
		return self.all().filter(is_standard = True)


CotationsManager = CotationsQuerySet.as_manager		


