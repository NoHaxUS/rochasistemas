import os
import sys
import django

def main():
    sys.path.append('C:\\DEV\\bet_bola\\bet_bola')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
    from utils import utils
    print("POPULATING")
    utils.populating_bd(3)
    print("POPULATING")


if __name__ == '__main__':
    main()
