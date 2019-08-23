import os
import sys
import django
import json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from user.models import CustomUser, Seller, Manager
from core.models import Store


def load_data():    
    store_id = 1
    file_address = "C:\\Users\Windows7\\Documents\\code\\old_bet_bola\\bet_bola\\bet_bola\\data.json"

    with open(file_address, "r") as out:
        data = out.read()
        if data:
            data = json.loads(data)                
    
    for instance in data:
        if instance["user_type"] == 3:
            if not Manager.objects.filter(username=instance['username']):
                Manager.objects.create(user_type=instance["user_type"],username=instance["username"],first_name=instance["first_name"],password=instance["password"],
                                    cellphone=instance["cellphone"],address=instance["address"],cpf=instance["cpf"],can_sell_unlimited=instance["can_sell_unlimited"],
                                    credit_limit=instance["credit_limit"],limit_time_to_cancel=instance["limit_time_to_cancel"],can_change_limit_time=instance["can_change_limit_time"],
                                    email=instance["email"],can_cancel_ticket=instance["can_cancel_ticket"],comission_based_on_profit=instance["comission_based_on_profit"],my_store=Store.objects.get(pk=store_id))
            else:
                username = change_username(instance["username"])
                while Manager.objects.filter(username=username):
                    username = change_username(instance["username"])

                data = change_manager_username(data, instance["username"], username)

                Manager.objects.create(user_type=instance["user_type"],username=username,first_name=instance["first_name"],password=instance["password"],
                                    cellphone=instance["cellphone"],address=instance["address"],cpf=instance["cpf"],can_sell_unlimited=instance["can_sell_unlimited"],
                                    credit_limit=instance["credit_limit"],limit_time_to_cancel=instance["limit_time_to_cancel"],can_change_limit_time=instance["can_change_limit_time"],
                                    email=instance["email"],can_cancel_ticket=instance["can_cancel_ticket"],comission_based_on_profit=instance["comission_based_on_profit"],my_store=Store.objects.get(pk=store_id))

    for instance in data:        
        if instance['user_type'] == 2:
            manager = instance["my_manager"]
            if not Seller.objects.filter(username=instance['username']):
                seller = Seller.objects.create(user_type=instance["user_type"],username=instance["username"],first_name=instance["first_name"],password=instance["password"],
                                    cellphone=instance["cellphone"],address=instance["address"],cpf=instance["cpf"],can_sell_unlimited=instance["can_sell_unlimited"],
                                    credit_limit=instance["credit_limit"],limit_time_to_cancel=instance["limit_time_to_cancel"],
                                    email=instance["email"],can_cancel_ticket=instance["can_cancel_ticket"],my_store=Store.objects.get(pk=store_id))                
            else:
                username = change_username(instance["username"])
                while Seller.objects.filter(username=username):
                    username = change_username(instance["username"])
                
                print("Usuario foi alterado de " + instance["username"] + " para " + username)

                seller = Seller.objects.create(user_type=instance["user_type"],username=username,first_name=instance["first_name"],password=instance["password"],
                                    cellphone=instance["cellphone"],address=instance["address"],cpf=instance["cpf"],can_sell_unlimited=instance["can_sell_unlimited"],
                                    credit_limit=instance["credit_limit"],limit_time_to_cancel=instance["limit_time_to_cancel"],
                                    email=instance["email"],can_cancel_ticket=instance["can_cancel_ticket"],my_store=Store.objects.get(pk=store_id))
            if manager:
                seller.my_manager=Manager.objects.filter(username=manager).first()
                seller.save()

def change_username(username):
    import re
    if re.match('.*?([0-9]+)$', username):
        number = re.match('.*?([0-9]+)$', username).group(1)
        return username.replace(number, str(int(number) + 1))
    return username + "1"    

def change_manager_username(data, old_username, new_username):
    for user in data:
        if user["user_type"] == 2 and user["my_manager"] == old_username:            
            user["my_manager"] = new_username
    print("Usuario foi alterado de " + old_username + " para " + new_username)
    return data

load_data()