import os
import sys
import django

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    from utils import update_games
    from utils.timezone import now
    
    print("Update Started.." + str(now()))
    update_games.consuming_championship_api()
    print("Finished Succesfully.")


if __name__ == '__main__':
    main()
