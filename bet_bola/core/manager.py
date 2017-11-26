from django.db.models.query import QuerySet
from django.db.models import Q

class GamesQuerySet(QuerySet):

	def able_games(self):
		return self.all().filter( Q(status_game="FT")| Q(status_game="NS")| Q(status_game="LIVE") | Q(status_game="HT") | Q(status_game="ET") 
			| Q(status_game="PT") | Q(status_game="BREAK") | Q(status_game="DELAYED"))

GamesManager = GamesQuerySet.as_manager