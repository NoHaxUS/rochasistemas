import os

os.system("git merge --no-ff --no-commit v6-prod --strategy-option theirs")

#settings
os.system("git reset HEAD bet_bola/config/settings.py")
os.system("git checkout -- bet_bola/config/settings.py")
#banner
os.system("git reset HEAD bet_bola/static/img/slider/banner.jpg")
os.system("git checkout -- bet_bola/static/img/slider/banner.jpg")
#cotation restrictions
os.system("git reset HEAD bet_bola/core/cotations_restrictions.py")
os.system("git checkout -- bet_bola/core/cotations_restrictions.py")
#home.js
#os.system("git reset HEAD bet_bola/static/js/home.js")
#os.system("git checkout -- bet_bola/static/js/home.js")
#main.css
os.system("git reset HEAD bet_bola/static/css/main.css")
os.system("git checkout -- bet_bola/static/css/main.css")