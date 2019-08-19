import requests
import datetime
import math
import time
import json
from core.models import Location, League, Sport, Market, Game, Cotation
from ticket.models import Ticket
from django.db.models import Q , Count
from updater.countries import COUNTRIES
from updater.ccs import COUNTRIES
from updater.sports import SPORTS
from updater.get_markets import (
    cotation_with_header_goals, 
    cotation_without_header, cotation_with_header_name_special, 
    cotation_with_header_opp, cotation_with_header_name, 
    cotation_without_header_standard
)


def get_games_of_the_day(current_url, error_count=0):
    print(current_url)
    request = requests.get(current_url)
    try:
        data = request.json()
        return data
    except json.decoder.JSONDecodeError:
        if error_count <= 4:
            error_count += 1
            get_games_of_the_day(current_url, error_count)

def get_games_of_current_page(current_url, error_count=0):
    print(current_url)
    request = requests.get(current_url)
    try:
        data = request.json()
        return data
    except json.decoder.JSONDecodeError:
        if error_count <= 4:
            error_count += 1
            get_games_of_current_page(current_url, error_count)

def get_upcoming_events():
    base_day = datetime.datetime.today()

    url_base = "https://api.betsapi.com/v1/bet365/upcoming?sport_id=1&token=20445-s1B9Vv6E9VSLU1&day={0}&page={1}"

    #for index in range(-1, 4):
    for index in range(-1, 3):
        page = 1
        current_date = (base_day + datetime.timedelta(days=index)).strftime('%Y%m%d')
        current_url = url_base.format(current_date, page)
        data = get_games_of_the_day(current_url)
        
        if data.get('success') and data.get('success') == 1:
            games_total = data['pager']['total']
            per_page = data['pager']['per_page']
            num_pages = math.ceil(int(games_total) / int(per_page))
            process_upcoming_events(data)
            page +=1
        else:
            print("Error on this url: " + current_url)

        while page <= num_pages:
            current_url = url_base.format(current_date, page)
            data = get_games_of_current_page(current_url)
            if data and data.get('success') and data.get('success') == 1:
                process_upcoming_events(data)
                page += 1
            else:
                print("Error on this url: " + current_url)


def get_cc_from_result(game_id, error_count=0):
    print("getting cc from result " + game_id)
    url = "https://api.betsapi.com/v1/bet365/result?token=20445-s1B9Vv6E9VSLU1&event_id=" + game_id
    request = requests.get(url)
    try:
        data = request.json()
        if request.status_code == 200 and data.get('success') and data.get('success') == 1:
            league = data['results'][0].get('league', None)
            if league:
                return league.get('cc', None)
        else:
            print("Error on get_cc_from url: " + url)
    except json.decoder.JSONDecodeError:
        if error_count <= 4:
            error_count += 1
            get_cc_from_result(game_id, error_count)
            


def get_game_name(game):
    return game['home']['name'] + ' x ' + game['away']['name']


def get_start_date_from_timestamp(game):
    return datetime.datetime.fromtimestamp(int(game['time']))


def get_league_and_create_location(game):
    league, created = League.objects.get_or_create(
        pk=int(game['league']['id']),
        defaults={
            'name': game['league']['name']
        }
    )

    if league.location == None:
        cc = get_cc_from_result(game['id'])
        country_translated = COUNTRIES.get(cc, None)

        if cc == None or country_translated == None:
            league.location = Location.objects.get_or_create(
                cc="inter",
                defaults={
                    'name': COUNTRIES.get('inter', "Internacional")
                }
            )[0]
        else:
            league.location = Location.objects.get_or_create(
                cc=cc,
                defaults={
                    'name': country_translated
                }
            )[0]
        
        league.save()
    return league

def get_sport(game):
    sport = Sport.objects.get_or_create(
        pk=int(game['sport_id']),
        defaults={
            'name': SPORTS.get(game['sport_id'], "Futebol")
        }
    )[0]
    return sport


def process_upcoming_events(data):
    if data['success'] == 1:
        game_ids = []
        for game in data['results']:
            game_name = get_game_name(game)
            print(game['id'] + ' - ' + game_name)
            Game.objects.get_or_create(
                pk=game['id'],
                defaults={
                    'name': game_name,
                    'home_team': game['home']['name'],
                    'away_team': game['away']['name'],
                    'start_date': get_start_date_from_timestamp(game),
                    'league': get_league_and_create_location(game),
                    'sport': get_sport(game),
                    'status': int(game['time_status'])
                }
            )
            game_ids.append(game['id'])    
        get_cotations(game_ids)


def get_cotations(games_ids, err_count=0):
    
    while games_ids:
        games_ids_str = ','.join(games_ids[:10])
        print("getting cotations for " + games_ids_str)
        url = "https://api.betsapi.com/v1/bet365/prematch?token=20445-s1B9Vv6E9VSLU1&FI=" + games_ids_str
        response = requests.get(url)
        try:
            data = response.json()
            if response.status_code == 200 and data['success'] == 1:

                for game_cotation in data['results']:

                    if game_cotation.get('goals', None):
                        get_goals_cotations(game_cotation['goals'], game_cotation['FI'])
                    if game_cotation.get('half', None):
                        get_half_cotations(game_cotation['half'], game_cotation['FI'])
                    if game_cotation.get('main', None):
                        get_main_cotations(game_cotation['main'], game_cotation['FI'])
                    if game_cotation.get('specials', None):
                        get_special_cotations(game_cotation['specials'], game_cotation['FI'])

                del games_ids[:10]

        except json.decoder.JSONDecodeError:
            if err_count <= 4:
                err_count += 1
                get_cotations(games_ids, err_count)


def get_special_cotations(special_cotations, game_id):
    if special_cotations.get('sp', None):
        if special_cotations['sp'].get('specials', None):
            cotation_with_header_name_special(special_cotations['sp']['specials'], 'specials', game_id)


def get_main_cotations(main_cotations, game_id):
    if main_cotations.get('sp', None):
        if main_cotations['sp'].get('full_time_result', None):
            cotation_without_header_standard(main_cotations['sp']['full_time_result'], 'full_time_result', game_id)
        if main_cotations['sp'].get('double_chance', None):
            cotation_without_header(main_cotations['sp']['double_chance'], 'double_chance', game_id)
        if main_cotations['sp'].get('correct_score', None):
            cotation_with_header_opp(main_cotations['sp']['correct_score'], 'correct_score', game_id)
        if main_cotations['sp'].get('half_time_full_time', None):
            cotation_without_header(main_cotations['sp']['half_time_full_time'], 'half_time_full_time', game_id)
        if main_cotations['sp'].get('draw_no_bet', None):
            cotation_without_header(main_cotations['sp']['draw_no_bet'], 'draw_no_bet', game_id)
        if main_cotations['sp'].get('result_both_teams_to_score', None):
            cotation_with_header_name(main_cotations['sp']['result_both_teams_to_score'], 'result_both_teams_to_score', game_id)
        if main_cotations['sp'].get('winning_margin', None):
            cotation_with_header_goals(main_cotations['sp']['winning_margin'], 'winning_margin', game_id)


def get_half_cotations(half_cotations, game_id):
    if half_cotations.get('sp', None):
        if half_cotations['sp'].get('half_time_result', None):
            cotation_without_header_standard(half_cotations['sp']['half_time_result'], 'half_time_result', game_id)
        if half_cotations['sp'].get('half_time_double_chance', None):
            cotation_without_header(half_cotations['sp']['half_time_double_chance'], 'half_time_double_chance', game_id)
        if half_cotations['sp'].get('half_time_result_both_teams_to_score', None):
            cotation_without_header(half_cotations['sp']['half_time_result_both_teams_to_score'], 'half_time_result_both_teams_to_score', game_id)
        if half_cotations['sp'].get('half_time_result_total_goals', None):
            cotation_without_header(half_cotations['sp']['half_time_result_total_goals'], 'half_time_result_total_goals', game_id, need_extract=True)
        if half_cotations['sp'].get('half_time_correct_score', None):
            cotation_with_header_opp(half_cotations['sp']['half_time_correct_score'], 'half_time_correct_score', game_id)
        if half_cotations['sp'].get('both_teams_to_score_in_1st_half', None):
            cotation_without_header(half_cotations['sp']['both_teams_to_score_in_1st_half'], 'both_teams_to_score_in_1st_half', game_id)
        if half_cotations['sp'].get('both_teams_to_score_in_2nd_half', None):
            cotation_without_header(half_cotations['sp']['both_teams_to_score_in_2nd_half'], 'both_teams_to_score_in_2nd_half', game_id)
        
        if half_cotations['sp'].get('both_teams_to_score_1st_half_2nd_half', None):
            cotation_without_header(half_cotations['sp']['both_teams_to_score_1st_half_2nd_half'], 'both_teams_to_score_1st_half_2nd_half', game_id)
        if half_cotations['sp'].get('first_half_goals', None):
            cotation_with_header_goals(half_cotations['sp']['first_half_goals'], 'first_half_goals', game_id)
        if half_cotations['sp'].get('exact_1st_half_goals', None):
            cotation_without_header(half_cotations['sp']['exact_1st_half_goals'], 'exact_1st_half_goals', game_id, need_extract=True)
        if half_cotations['sp'].get('1st_half_goals_odd_even', None):
            cotation_without_header(half_cotations['sp']['1st_half_goals_odd_even'], '1st_half_goals_odd_even', game_id)
        if half_cotations['sp'].get('to_score_in_half', None):
            cotation_with_header_name(half_cotations['sp']['to_score_in_half'], 'to_score_in_half', game_id)
        if half_cotations['sp'].get('half_with_most_goals', None):
            cotation_without_header(half_cotations['sp']['half_with_most_goals'], 'half_with_most_goals', game_id)
        
        if half_cotations['sp'].get('home_team_highest_scoring_half', None):
            cotation_without_header(half_cotations['sp']['home_team_highest_scoring_half'], 'home_team_highest_scoring_half', game_id)
        if half_cotations['sp'].get('away_team_highest_scoring_half', None):
            cotation_without_header(half_cotations['sp']['away_team_highest_scoring_half'], 'away_team_highest_scoring_half', game_id)
        if half_cotations['sp'].get('2nd_half_result', None):
            cotation_without_header_standard(half_cotations['sp']['2nd_half_result'], '2nd_half_result', game_id)
        if half_cotations['sp'].get('2nd_half_goals', None):
            cotation_with_header_goals(half_cotations['sp']['2nd_half_goals'], '2nd_half_goals', game_id)
        if half_cotations['sp'].get('exact_2nd_half_goals', None):
            cotation_without_header(half_cotations['sp']['exact_2nd_half_goals'], 'exact_2nd_half_goals', game_id, need_extract=True)
        if half_cotations['sp'].get('2nd_half_goals_odd_even', None):
            cotation_without_header(half_cotations['sp']['2nd_half_goals_odd_even'], '2nd_half_goals_odd_even', game_id)


def get_goals_cotations(goals_cotations, game_id):
    if goals_cotations.get('sp', None):
        if goals_cotations['sp'].get('goals_over_under', None):
            cotation_with_header_goals(goals_cotations['sp']['goals_over_under'], 'goals_over_under', game_id)
        if goals_cotations['sp'].get('alternative_total_goals', None):
            cotation_with_header_goals(goals_cotations['sp']['alternative_total_goals'], 'alternative_total_goals', game_id)

        if goals_cotations['sp'].get('result_total_goals', None):
            cotation_without_header(goals_cotations['sp']['result_total_goals'], 'result_total_goals', game_id, need_extract=True)
        if goals_cotations['sp'].get('total_goals_both_teams_to_score', None):
            cotation_without_header(goals_cotations['sp']['total_goals_both_teams_to_score'], 'total_goals_both_teams_to_score', game_id, need_extract=True)
        if goals_cotations['sp'].get('exact_total_goals', None):
            cotation_without_header(goals_cotations['sp']['exact_total_goals'], 'exact_total_goals', game_id, need_extract=True)
        
        #if goals_cotations['sp'].get('number_of_goals_in_match', None):
        #    cotation_without_header(goals_cotations['sp']['number_of_goals_in_match'], 'number_of_goals_in_match', game_id)
        
        if goals_cotations['sp'].get('both_teams_to_score', None):
            cotation_without_header(goals_cotations['sp']['both_teams_to_score'], 'both_teams_to_score', game_id)
        if goals_cotations['sp'].get('teams_to_score', None):
            cotation_without_header(goals_cotations['sp']['teams_to_score'], 'teams_to_score', game_id)
    
        if goals_cotations['sp'].get('home_team_exact_goals', None):
            cotation_without_header(goals_cotations['sp']['home_team_exact_goals'], 'home_team_exact_goals', game_id, need_extract=True)
        if goals_cotations['sp'].get('away_team_exact_goals', None):
            cotation_without_header(goals_cotations['sp']['away_team_exact_goals'], 'away_team_exact_goals', game_id, need_extract=True)
        if goals_cotations['sp'].get('goals_odd_even', None):
            cotation_without_header(goals_cotations['sp']['goals_odd_even'], 'goals_odd_even', game_id)
        if goals_cotations['sp'].get('home_team_odd_even_goals', None):
            cotation_without_header(goals_cotations['sp']['home_team_odd_even_goals'], 'home_team_odd_even_goals', game_id)
        if goals_cotations['sp'].get('away_team_odd_even_goals', None):
            cotation_without_header(goals_cotations['sp']['away_team_odd_even_goals'], 'away_team_odd_even_goals', game_id)



