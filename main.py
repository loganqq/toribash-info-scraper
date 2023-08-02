import os
import time
import datetime
import argparse
import hashlib
import requests
import threading

from bs4 import BeautifulSoup

from tb import Player
from tb.args import namespace

from dotenv import load_dotenv
load_dotenv('N:\\tb-duel-scrape\\.env')


total_bet_profit = 0
num_bets = 0
total_tc_bet = 0

total_duel_profit = 0
num_duels = 0
total_tc_dueled = 0


if __name__ == '__main__':

    start = time.time()

    print(f'Getting {namespace.action} information for:')
    print(*namespace.player, sep=', ')

    for index, obj in enumerate(namespace.player):
        player = Player(namespace.player[index])
        player.auth()

        match namespace.action:
            case 'bet':
                thread = threading.Thread(target=player.get_bet_profit)
                thread.start()

                thread.join()

                total_bet_profit += player.bet_profit
                num_bets += player.num_bets
                total_tc_bet += player.gross_tc_bet

            case 'duel':
                thread = threading.Thread(target=player.get_duel_profit)
                thread.start()

                thread.join()

                total_duel_profit += player.duel_profit
                num_duels += player.num_duels
                total_tc_dueled += player.gross_tc_dueled

            case _:
                print('Invalid option')
                exit(1)
    
    if namespace.action == 'bet':
        print(f'Results for', *namespace.player, ':')
        print(f'Profit: {total_bet_profit}')
        print(f'Total bets placed: {num_bets}')
        print(f'Total TC bet: {total_tc_bet}')

    elif namespace.action == 'duel':
        print(f'Results for', *namespace.player, ':')
        print(f'Profit: {total_duel_profit}')
        print(f'Total duels played: {num_duels}')
        print(f'Total TC dueled: {total_tc_dueled}')




    end = time.time()
    total_time = end - start
    total_time = datetime.timedelta(seconds=total_time)

    print(f'Script took: {total_time}')
