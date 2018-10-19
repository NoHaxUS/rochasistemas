import os
import sys
import django

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    from utils.new_update import get_locations, get_leagues, get_events, get_sports, start_consuming_updates
    from utils.timezone import now
    
    start_consuming_updates()

    print("Update Started.." + str(now()))
    # get_locations()
    # get_sports()
    # get_leagues()
    #get_events()
    print("Finished Succesfully.")


if __name__ == '__main__':
    main()
