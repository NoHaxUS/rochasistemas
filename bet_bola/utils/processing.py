import requests
from core.models import Game, Cotation, Championship, Ticket, Country, Market
from utils.models import GeneralConfigurations
import utils.timezone as tzlocal
import datetime
from django.db.models import Count
from django.db.models import F, Q
import time
from decimal import Decimal




def processing_cotations_v2():

    print("Processando resultados")

    games_to_process = Game.objects.annotate(cotations_count=Count('cotations'))\
        .filter(cotations_count__gt=0,
        ft_score__isnull=False,
        odds_processed=False)\
        .exclude(ft_score='')\
        .exclude(ft_score='-')\
        .exclude(ft_score='0')\

        
    print(games_to_process.count(), '\n')

    for game in games_to_process:

        print("Jogo:" + str(game.name) + " ID: " + str(game.pk))

        not_calculaded_cotations = game.cotations
        if game.ft_score and game.ft_score.strip() != '-':
            
            local_score_ft = int(game.ft_score.split('-')[0])
            visitor_score_ft = int(game.ft_score.split('-')[1])

            vencedor_encontro(game, not_calculaded_cotations, local_score_ft, visitor_score_ft)
            casa_visitante(game, not_calculaded_cotations, local_score_ft, visitor_score_ft)
            dupla_chance(game, not_calculaded_cotations, local_score_ft, visitor_score_ft)
            vencer_e_nao_tomar_gol(game, not_calculaded_cotations, local_score_ft, visitor_score_ft)
            numero_exato_de_gols(game, not_calculaded_cotations, local_score_ft, visitor_score_ft)
            resultado_e_2_times_marcam(game, not_calculaded_cotations, local_score_ft, visitor_score_ft)
            resultado_e_total_de_gols(game, not_calculaded_cotations, local_score_ft, visitor_score_ft)
            total_de_gols_impar_par(game, not_calculaded_cotations, local_score_ft, visitor_score_ft)
            os_dois_times_marcam(game, not_calculaded_cotations, local_score_ft, visitor_score_ft)
            total_gols_visitante(game, not_calculaded_cotations, local_score_ft, visitor_score_ft)
            total_gols_casa(game, not_calculaded_cotations, local_score_ft, visitor_score_ft)
            resultado_exato_jogo(game, not_calculaded_cotations, local_score_ft, visitor_score_ft)
            visitante_marca_pelo_menos_um_gol(game, not_calculaded_cotations, local_score_ft, visitor_score_ft)
            total_gols_encontro_acima_abaixo(game, not_calculaded_cotations, local_score_ft, visitor_score_ft)
            time_casa_nao_tomara_gols(game, not_calculaded_cotations, local_score_ft, visitor_score_ft)
            time_visitante_nao_tomara_gols(game, not_calculaded_cotations, local_score_ft, visitor_score_ft)
            time_casa_marca(game, not_calculaded_cotations, local_score_ft, visitor_score_ft)

        
        if game.ht_score and game.ht_score.strip() != '-' and game.ht_score.strip() != '0':

            local_score_ht = int(game.ht_score.split('-')[0])
            visitor_score_ht = int(game.ht_score.split('-')[1])

            vencedor_segundo_tempo(game, not_calculaded_cotations)
            total_gols_segundo_tempo_acima_abaixo(game, not_calculaded_cotations)
            etapa_com_mais_gol(game, not_calculaded_cotations, local_score_ht, visitor_score_ht)
            vencedor_nas_duas_etapas(game, not_calculaded_cotations, local_score_ht, visitor_score_ht)
            resultado_exato_primeiro_tempo(game, not_calculaded_cotations)
            vencedor_primeiro_tempo(game, not_calculaded_cotations, local_score_ht, visitor_score_ht)
            total_gols_primeiro_tempo_acima_abaixo(game, not_calculaded_cotations, local_score_ht, visitor_score_ht)

        game.odds_processed=True
        game.save()


def vencedor_encontro(game,all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind__pk=1)
    

    if cotations.count() > 0:
        cotations.update(winning=False)

        if local_team_score > visitor_team_score:
            cotations.filter(name='1').update(winning=True)			
        elif local_team_score < visitor_team_score:			
            cotations.filter(name='2').update(winning=True)			
        else:	
            cotations.filter(name='X').update(winning=True)


def casa_visitante(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind__pk=10)
    
    if cotations.count() > 0:
        cotations.update(winning=False)

        if local_team_score > visitor_team_score:
            cotations.filter(name='1').update(winning=True)
        elif local_team_score < visitor_team_score:		
            cotations.filter(name='2').update(winning=True)


def dupla_chance(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind__pk=63)

    if cotations.count() > 0:
        cotations.update(winning=False)
        casa_empate = cotations.filter(name='1X')
        casa_empate_nome = cotations.filter(name='Casa/Empate')
        casa_visitante = cotations.filter(name='12')
        casa_visitante_nome = cotations.filter(name='Casa/Visitante')
        empate_visitante = cotations.filter(name='X2')
        empate_visitante_nome = cotations.filter(name='Empate/Visitante')
    
        if local_team_score > visitor_team_score:
            casa_empate.update(winning=True)
            casa_empate_nome.update(winning=True)
            casa_visitante.update(winning=True)
            casa_visitante_nome.update(winning=True)
        elif local_team_score < visitor_team_score:
            casa_visitante.update(winning=True)
            casa_visitante_nome.update(winning=True)
            empate_visitante.update(winning=True)
            empate_visitante_nome.update(winning=True)
        else:
            casa_empate.update(winning=True)
            casa_empate_nome.update(winning=True)
            empate_visitante.update(winning=True)
            empate_visitante_nome.update(winning=True)


def vencer_e_nao_tomar_gol(game, all_cotations,local_team_score,visitor_team_score):
    
    cotations = all_cotations.filter(kind__pk=976236)

    if cotations.count() > 0:
        cotations.update(winning=False)
        if local_team_score > visitor_team_score:
            if visitor_team_score == 0:
                cotations.filter(name='1').update(winning=True)
        elif local_team_score < visitor_team_score:
            if local_team_score == 0:
                cotations.filter(name='2').update(winning=True)   


def etapa_com_mais_gol(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind__pk=976144)


    if cotations.count() > 0:

        casa_placar_1, visitante_placar_1 = (local_team_score, visitor_team_score)
        casa_placar_2, visitante_placar_2 = game.ft_score.split('-')
        result_1_etapa = int(casa_placar_1) +  int(visitante_placar_1)
        result_2_etapa = ( int(casa_placar_2) + int(visitante_placar_2) ) - result_1_etapa
        cotations.update(winning=False)

        if result_1_etapa > result_2_etapa:        
            cotations.filter(name='1° Tempo').update(winning=True)                                              
        elif result_1_etapa < result_2_etapa:                            
            cotations.filter(name='2° Tempo').update(winning=True)                      
        else:                        
            cotations.filter(name='X').update(winning=True)                     


def vencedor_nas_duas_etapas(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind__pk=976193)

    
    if cotations.count() > 0:

        casa_placar_1, visitante_placar_1 = (local_team_score, visitor_team_score)
        casa_placar_2, visitante_placar_2 = game.ft_score.split('-')
        result_1_etapa = int(casa_placar_1) - int(visitante_placar_1)
        result_2_etapa = int(casa_placar_2) - int(visitante_placar_2)
        cotations.update(winning=False)

        if result_1_etapa > 0 and result_2_etapa > 0:           
            cotations.filter(name='1').update(winning=True)

        elif result_1_etapa < 0 and result_2_etapa < 0:        
            cotations.filter(name='2').update(winning=True)             


def numero_exato_de_gols(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind__pk=976241)

    if cotations.count() > 0:
        
        casa_placar, visitante_placar = (local_team_score,visitor_team_score)
        result = int(casa_placar) + int(visitante_placar)
        cotations.update(winning=False)

        if result > 7:        
            cotations.filter(name='Mais de 7').update(winning=True)
        else:
            cotations.filter(name=str(result)).update(winning=True)    



def resultado_e_2_times_marcam(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind__pk=976316)

    
    if cotations.count() > 0:

        casa_placar, visitante_placar = (local_team_score,visitor_team_score)
        result = int(casa_placar) - int(visitante_placar)
        cotations.update(winning=False)

        if result > 0:
            if local_team_score > 0 and visitor_team_score > 0:                                   
                cotations.filter(name="Casa/Sim").update(winning=True)                          

            else:            
                cotations.filter(name="Casa/Não").update(winning=True)

        elif result < 0:
            if local_team_score > 0 and visitor_team_score > 0:                                   
                cotations.filter(name="Visitante/Sim").update(winning=True)
                
            else:
                cotations.filter(name="Visitante/Não").update(winning=True)                         

        else:
            if local_team_score > 0 and visitor_team_score > 0:                                   
                cotations.filter(name="Empate/Sim").update(winning=True)

            else:            
                cotations.filter(name="Empate/Não").update(winning=True)                            


def resultado_e_total_de_gols(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind__pk=976334)

    if cotations.count() > 0:
        casa_placar, visitante_placar = (local_team_score,visitor_team_score)
        result = int(casa_placar) - int(visitante_placar)
        total_gols = int(casa_placar) + int(visitante_placar)
        cotations.update(winning=False)

        if result > 0:
            cotations.filter(name__contains="Casa/Acima", total__lt=total_gols).update(winning=True)
            cotations.filter(name__contains="Casa/Abaixo", total__gt=total_gols).update(winning=True)
        elif result < 0:
            cotations.filter(name__contains="Visitante/Acima", total__lt=total_gols).update(winning=True)
            cotations.filter(name__contains="Visitante/Abaixo", total__gt=total_gols).update(winning=True)
        else:
            cotations.filter(name__contains="Empate/Acima", total__lt=total_gols).update(winning=True)
            cotations.filter(name__contains="Empate/Abaixo", total__gt=total_gols).update(winning=True)          


def total_de_gols_impar_par(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind__pk=975930)
           
    if cotations.count() > 0:

        total_gols = int((local_team_score,visitor_team_score)[0]) + int((local_team_score,visitor_team_score)[1])
        cotations.update(winning=False)

        if total_gols == 0 or total_gols % 2 == 0:
            cotations.filter(name="Par").update(winning=True)
        else:
            cotations.filter(name="Impar").update(winning=True)


def resultado_exato_primeiro_tempo(game, all_cotations):

    cotations = all_cotations.filter(kind__pk=975916)

    if cotations.count() > 0:
        cotations.update(winning=False)
        etapa_1_resultado = game.ht_score.replace('-',':').strip()
        winners = cotations.filter(name=etapa_1_resultado)
        winners.update(winning=True)


def os_dois_times_marcam(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind__pk=59)

    if cotations.count() > 0:
        cotations.update(winning=False)

        if local_team_score > 0 and visitor_team_score > 0:
            cotations.filter(name='Sim').update(winning=True)
        else:
            cotations.filter(name='Não').update(winning=True)


def vencedor_primeiro_tempo(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind__pk=37)

    if cotations.count() > 0:
        cotations.update(winning=False)

        casa_placar, visita_placar = (local_team_score, visitor_team_score)

        if casa_placar > visita_placar:
            cotations.filter(name='1').update(winning=True)
        elif casa_placar < visita_placar:
            cotations.filter(name='2').update(winning=True)
        else:
            cotations.filter(name='X').update(winning=True)


def total_gols_visitante(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind__pk=976204)

    if cotations.count() > 0:
        cotations.update(winning=False)
        cotations.filter(name__contains='Acima', total__lt=visitor_team_score).update(winning=True)
        cotations.filter(name__contains='Abaixo', total__gt=visitor_team_score).update(winning=True)


def total_gols_casa(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind__pk=976198)

    if cotations.count() > 0:
        cotations.update(winning=False)
        cotations.filter(name__contains='Acima', total__lt=local_team_score).update(winning=True)
        cotations.filter(name__contains='Abaixo', total__gt=local_team_score).update(winning=True)


def total_gols_primeiro_tempo_acima_abaixo(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind__pk=38)

    if cotations.count() > 0:
        cotations.update(winning=False)
        casa_placar, visita_placar = (local_team_score,visitor_team_score)
        placar_total_etapa_1 = int(casa_placar) + int(visita_placar)
        
        cotations.filter(name__contains='Acima', total__lt=placar_total_etapa_1).update(winning=True)
        cotations.filter(name__contains='Abaixo', total__gt=placar_total_etapa_1).update(winning=True)



def resultado_exato_jogo(game, all_cotations,local_team_score,visitor_team_score):
    cotations = all_cotations.filter(kind__pk=975909)

    if cotations.count() > 0:
        result_ft = game.ft_score.replace('-',':')
        cotations.update(winning=False)
        winners = cotations.filter(name=result_ft)
        winners.update(winning=True)


def visitante_marca_pelo_menos_um_gol(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind__pk=976360)

    if cotations.count() > 0:
        cotations.update(winning=False)
        if visitor_team_score > 0:
            cotations.filter(name='Sim').update(winning=True)
        else:
            cotations.filter(name='Não').update(winning=True)


def total_gols_encontro_acima_abaixo(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind__pk=12)

    if cotations.count() > 0:
        cotations.update(winning=False)
        casa_placar, visita_placar = (local_team_score,visitor_team_score)
        placar_total = int(casa_placar) + int(visita_placar)
        
        cotations.filter(name__contains='Acima', total__lt=placar_total).update(winning=True)
        cotations.filter(name__contains='Abaixo', total__gt=placar_total).update(winning=True)


def time_casa_nao_tomara_gols(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind__pk=976096)

    if cotations.count() > 0:
        cotations.update(winning=False)

        if visitor_team_score > 0:
            cotations.filter(name='Não').update(winning=True)
        else:
            cotations.filter(name='Sim').update(winning=True)


def time_visitante_nao_tomara_gols(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind__pk=8594683)

    if cotations.count() > 0:
        cotations.update(winning=False)

        if local_team_score > 0:
            cotations.filter(name='Não').update(winning=True)
        else:
            cotations.filter(name='Sim').update(winning=True)



def time_casa_marca(game, all_cotations,local_team_score,visitor_team_score):

    cotations = all_cotations.filter(kind__pk=976348)

    if cotations.count() > 0:
        cotations.update(winning=False)

        if local_team_score > 0:
            cotations.filter(name='Sim').update(winning=True)
        else:
            cotations.filter(name='Não').update(winning=True)



def vencedor_segundo_tempo(game, all_cotations):

    cotations = all_cotations.filter(kind__pk=80)

    if cotations.count() > 0:
        cotations.update(winning=False)

        casa_placar_ht = int(game.ht_score.split('-')[0])
        visita_placar_ht = int(game.ht_score.split('-')[1])

        casa_placar_ft = int(game.ft_score.split('-')[0])
        visita_placar_ft = int(game.ft_score.split('-')[1])

        casa_placar_segundo_tempo = casa_placar_ft - casa_placar_ht
        visita_placar_segundo_tempo = visita_placar_ft - visita_placar_ht

        if casa_placar_segundo_tempo > visita_placar_segundo_tempo:
            cotations.filter(name='1').update(winning=True)
        elif casa_placar_segundo_tempo < visita_placar_segundo_tempo:
            cotations.filter(name='2').update(winning=True)
        else:
            cotations.filter(name='X').update(winning=True)


def total_gols_segundo_tempo_acima_abaixo(game, all_cotations):

    cotations = all_cotations.filter(kind__pk=47)

    if cotations.count() > 0:
        cotations.update(winning=False)
  
        casa_placar_ht = int(game.ht_score.split('-')[0])
        visita_placar_ht = int(game.ht_score.split('-')[1])

        casa_placar_ft = int(game.ft_score.split('-')[0])
        visita_placar_ft = int(game.ft_score.split('-')[1])

        casa_placar_segundo_tempo = casa_placar_ft - casa_placar_ht
        visita_placar_segundo_tempo = visita_placar_ft - visita_placar_ht

        placar_total_etapa_2 = casa_placar_segundo_tempo + visita_placar_segundo_tempo

        cotations.filter(name__contains='Acima', total__lt=placar_total_etapa_2).update(winning=True)
        cotations.filter(name__contains='Abaixo', total__gt=placar_total_etapa_2).update(winning=True)



def process_tickets():
    tickets_to_process = Ticket.objects.filter(bet_ticket_status='Aguardando Resultados')
    for ticket in tickets_to_process:
        ticket.update_ticket_status()
