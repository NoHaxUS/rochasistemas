import os

with open('config.sites', 'r') as file:
    for line in file:
        sitename = line.split('|')[1]
        print("Site: " + sitename)
        
        os.system("git co " + sitename)
        #os.system("git diff HEAD~5:bet_bola/core/views.py HEAD:bet_bola/core/views.py")
        input("Aperte para continuar")
        os.system('git commit -am \"OK\"')
        os.system("git push origin " + sitename)
        print("OK")
