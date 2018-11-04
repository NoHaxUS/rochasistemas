import pika
import json
import requests
from .update import get_events, get_leagues, get_locations, get_sports
from core.models import Location, League, Sport, Market, Period, Game, Cotation
from .real_time import process_fixture_metadata, process_markets_realtime, process_settlements


def write_logs(msg):
    with open('logs.log', 'a+') as file:
        file.write(msg + "\n")

def start_update():  
    write_logs("Update Started...")
    get_sports()
    get_locations()
    get_leagues()
    get_events()
    write_logs("Fininshing Update...")


def on_message(channel, method_frame, header_frame, body):

    json_parsed = json.loads(body.decode())
    type_res = int(json_parsed['Header']['Type'])

    if type_res == 1:
        process_fixture_metadata(json_parsed)
    #elif type_res == 3:
    #    process_markets_realtime(json_parsed)
    elif type_res == 35:
        process_settlements(json_parsed)
    
    channel.basic_ack(method_frame.delivery_tag)


def activate_package():
    requests.get("http://prematch.lsports.eu/OddService/EnablePackage?username=pabllobeg1@gmail.com&password=cdfxscsdf45f23&guid=cbc4e422-1f53-4856-9c01-a4f8c428cb54")


def start_consuming_updates():
    parameters = pika.ConnectionParameters(host='localhost')
    connection = pika.BlockingConnection(parameters=parameters)
    channel = connection.channel()

    channel.exchange_declare(exchange='relay',
                            exchange_type='fanout')

    result = channel.queue_declare(exclusive=True)

    queue_name = result.method.queue

    channel.queue_bind(exchange='relay', queue=queue_name)

    channel.basic_consume(on_message, queue=queue_name)

    try:
        activate_package()
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()
    