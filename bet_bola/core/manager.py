from django.db.models.query import QuerySet
from django.db.models import Q
from django.db.models import Count
from django.db import models
import utils.timezone as tzlocal
from django.utils import timezone


class GamesQuerySet(QuerySet):

	def able_games(self):
		return self.annotate(cotations_count=Count('cotations', filter=Q(cotations__is_standard=True))).filter(cotations_count__gte=3).filter(Q(status_game="NS") | Q(status_game="POSTP")).filter(start_game_date__gt=tzlocal.now())

	def today_able_games(self):
		return self.annotate(cotations_count=Count('cotations' , filter=Q(cotations__is_standard=True))).filter(cotations_count__gte=3).filter(Q(status_game="NS") | Q(status_game="POSTP")).filter(start_game_date__gt=tzlocal.now()).filter(start_game_date__lt=(tzlocal.now().date() + timezone.timedelta(days=1)) )

	def tomorrow_able_games(self):
		return self.annotate(cotations_count=Count('cotations' , filter=Q(cotations__is_standard=True))).filter(cotations_count__gte=3).filter(Q(status_game="NS") | Q(status_game="POSTP")).filter(start_game_date__date=tzlocal.now().date() + timezone.timedelta(days=1) )

GamesManager = GamesQuerySet.as_manager

class CotationsQuerySet(QuerySet):

	def standard_cotations(self):
		return self.filter(is_standard = True)


CotationsManager = CotationsQuerySet.as_manager		


