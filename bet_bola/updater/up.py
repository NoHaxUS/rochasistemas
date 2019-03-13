import pika
import json
import requests
from .update import get_upcoming_events
#from core.models import Location, League, Sport, Market, Period, Game, Cotation
#from .real_time import process_fixture_metadata, process_markets_realtime, process_settlements


def write_logs(msg):
    with open('logs.log', 'a+') as file:
        file.write(msg + "\n")

def start_update():
    get_upcoming_events()

