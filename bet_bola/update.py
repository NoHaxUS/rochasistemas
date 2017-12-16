import os
import sys
import django

def main():
    sys.path.append('C:\\DEV\\bet_bola\\bet_bola')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
    from utils import utils
    print("UPDATING")
    utils.updating_games()
    print("UPDATING")


if __name__ == '__main__':
    main()
