import os
import sys
import django

def main():
    #sys.path.append('C:\\DEV\\bet_bola2\\bet_bola')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
    from utils import up_new
    print("Start")
    up_new.consuming_championship_api()
    print("End")


if __name__ == '__main__':
    main()
