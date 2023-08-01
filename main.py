import os
import time
import datetime
import argparse
import hashlib
import requests

from bs4 import BeautifulSoup

from tb import Player
from tb.args import namespace

from dotenv import load_dotenv
load_dotenv('N:\\tb-duel-scrape\\.env')


if __name__ == '__main__':
    player = Player(namespace.player)
    player.auth()

    start = time.time()

    print(f'Getting {namespace.action} information for {player.username}')

    match namespace.action:
        case 'bet':
            player.get_bet_profit()
        case 'duel':
            player.get_duel_profit()
        case 'summer_2023':
            player.get_summer_lottery_info()
        case _:
            exit(1)

    end = time.time()
    total_time = end - start
    total_time = datetime.timedelta(seconds=total_time)

    print(f'Script took: {total_time}')
