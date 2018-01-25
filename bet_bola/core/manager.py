from django.db.models.query import QuerySet
from django.db.models import Q
from django.db.models import Count
import utils.timezone as tzlocal
from django.utils import timezone


class GamesQuerySet(QuerySet):


	def able_games(self):
		return self.annotate(cotations_count=Count('cotations')).filter(cotations_count__gt=0).filter(status_game="NS").filter(start_game_date__gte=tzlocal.now())

	def today_able_games(self):
		return self.annotate(cotations_count=Count('cotations')).filter(cotations_count__gt=0).filter(status_game="NS").filter(start_game_date__gte=tzlocal.now()).filter(start_game_date__lte=(tzlocal.now() + timezone.timedelta(days=1)) )

	def tomorrow_able_games(self):
		return self.annotate(cotations_count=Count('cotations')).filter(cotations_count__gt=0).filter(status_game="NS").filter(start_game_date__date=tzlocal.now().date() + timezone.timedelta(days=1) )

GamesManager = GamesQuerySet.as_manager


class CotationsQuerySet(QuerySet):

	def standard_cotations(self):
		return self.all().filter(is_standard = True)


CotationsManager = CotationsQuerySet.as_manager		


