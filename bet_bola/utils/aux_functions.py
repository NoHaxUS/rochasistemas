from .choices import COUNTRY_TRANSLATE, MARKET_ID, MARKET_NAME_SMALL_TEAMS, INVALID_ALL_COTES_CHAMPIONSHIPS
import urllib3
import socket
from utils.models import GeneralConfigurations, MarketReduction

def allowed_gai_family():
    family = socket.AF_INET
    return family

urllib3.util.connection.allowed_gai_family = allowed_gai_family

def get_country_translated(country_name):
    return COUNTRY_TRANSLATE.get(country_name, country_name)

def renaming_cotations(string):

    COTATION_NAME = {
        "Under": "Abaixo",
        "Over": "Acima",
        "Draw": "Empate",
        "Away": "Visitante",
        "Home": "Casa",
        "1st Half": "1° Tempo",
        "2nd Half": "2° Tempo",
        "No": "Não",
        "Yes": "Sim",
        "More": "Mais de",
        "Odd": "Impar",
        "Even" : "Par",
        "more" : "Mais de"
    }

    for key_cotation in COTATION_NAME.keys():
        if key_cotation in string:
            string = string.replace(key_cotation, COTATION_NAME[key_cotation])
    return string



def check_request_status(request):
    if not request.status_code == 200:
        print('Falha: Url:' + request.url)
        print('Status: ' + request.status_code)



def get_bet365_from_bookmakers(bookmakers):

    for bookmaker in bookmakers:
        if int(bookmaker['id']) == 2:
            return bookmaker
    return bookmakers[0]


def can_save_this_market(kind_name, championship_id, processed_markets):

    if kind_name in MARKET_ID.values():
        if championship_id in INVALID_ALL_COTES_CHAMPIONSHIPS:
            if kind_name in MARKET_NAME_SMALL_TEAMS.values() and kind_name not in processed_markets:                
                return True
        elif kind_name not in processed_markets:
            return True
    return False


def set_cotations_reductions():
    if GeneralConfigurations.objects.filter(pk=1).exists():
        print("Processando Redução de Cotas Geral")
        GeneralConfigurations.objects.get(pk=1).apply_reductions()
    
    market_reductions = MarketReduction.objects.all()
    for market_reduction in market_reductions:
        print("Processando Redução: " + str(market_reduction.market_to_reduct))
        market_reduction.apply_reductions() 
        
