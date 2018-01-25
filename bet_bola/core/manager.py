from django.db.models.query import QuerySet
from django.db.models import Q
from django.db.models import Count
from django.utils import timezone
import datetime


def get_time_now():
	return timezone.now() - timezone.timedelta(hours=2)

class GamesQuerySet(QuerySet):


	def able_games(self):
		return self.annotate(cotations_count=Count('cotations')).filter(cotations_count__gt=0).filter(status_game="NS").filter(start_game_date__gte=get_time_now())

	def today_able_games(self):
		return self.annotate(cotations_count=Count('cotations')).filter(cotations_count__gt=0).filter(status_game="NS").filter(start_game_date__gte=get_time_now() ).filter(start_game_date__lte=(get_time_now() + timezone.timedelta(days=1)) )

	def tomorrow_able_games(self):
		return self.annotate(cotations_count=Count('cotations')).filter(cotations_count__gt=0).filter(status_game="NS").filter(start_game_date__date=get_time_now().date() + timezone.timedelta(days=1) )

GamesManager = GamesQuerySet.as_manager


class CotationsQuerySet(QuerySet):

	def standard_cotations(self):
		return self.all().filter(is_standard = True)


CotationsManager = CotationsQuerySet.as_manager		


