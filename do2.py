import os

with open('config.sites', 'r') as file:
    for line in file:
        sitename = line.split('|')[1]
        print("Site: " + sitename)
        
        os.system("git co " + sitename)
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

        #new logo
        os.system("git reset HEAD bet_bola/static/bootstrap_admin/img/logo-140x60.png")
        os.system("git checkout -- bet_bola/static/bootstrap_admin/img/logo-140x60.png")
         
        #new logo small
        os.system("git reset HEAD bet_bola/static/bootstrap_admin/img/logo-small.png")
        os.system("git checkout -- bet_bola/static/bootstrap_admin/img/logo-small.png")

        #home.js
        os.system("git reset HEAD bet_bola/static/js/home.js")
        os.system("git checkout -- bet_bola/static/js/home.js")
        #main.css
        os.system("git reset HEAD bet_bola/static/css/main.css")
        os.system("git checkout -- bet_bola/static/css/main.css")
        os.system('git commit -am \"OK\"')
        os.system("git push origin " + sitename)
        print("OK")
