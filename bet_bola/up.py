import os
import sys
import django

def main():
    from utils import update_games
    from utils.timezone import now

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
    
    print("Update Started.." + now())
    update_games.consuming_championship_api()
    print("Finished Succesfully.")


if __name__ == '__main__':
    main()
