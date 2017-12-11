from django.db.models.query import QuerySet
from django.db.models import Q
from django.db.models import Count

class GamesQuerySet(QuerySet):

	def able_games(self):

		return self.all().annotate(cotations_count=Count('cotations')).filter(cotations_count__gt=0).filter( Q(status_game="FT")| Q(status_game="NS")| Q(status_game="LIVE") | Q(status_game="HT") | Q(status_game="ET") 
			| Q(status_game="PT") | Q(status_game="BREAK") | Q(status_game="DELAYED"))
																					

GamesManager = GamesQuerySet.as_manager


class CotationsQuerySet(QuerySet):

	def standard_cotations(self):
		return self.all().filter(is_standard = True)


CotationsManager = CotationsQuerySet.as_manager		


