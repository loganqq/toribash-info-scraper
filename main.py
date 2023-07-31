import os
import time
import datetime
import argparse
import hashlib
import requests

from bs4 import BeautifulSoup

from tb import Player

from dotenv import load_dotenv
load_dotenv('N:\\tb-duel-scrape\\.env')


parser = argparse.ArgumentParser()

parser.add_argument(
    'action',
    type=str,
    choices=['bet', 'duel', 'summer-2023'],
    help='action'
)
parser.add_argument(
    'player',
    type=str
)
namespace = parser.parse_args()


def summer_lottery(player):
    global user_id
    global total_volume

    total_volume = 0

    summer_categories = ['Summer Lottery 2023 - Epic Ticket', 'Summer Lottery 2023 - Mystery Ticket', 'Summer Lottery 2023 - 10 Cheap and Sunburnt Ticket', 'Summer Lottery 2023 - 10 Luxury Tickets (Discount)']

    response = SESSION.get(f"https://forum.toribash.com/tori_stats.php?username={player}&format=json")
    user_stats = response.json()
    user_id = user_stats["userid"]

    print('ID:', user_id)

    r = SESSION.get(f'https://forum.toribash.com/tori_trans_hist.php?userid={user_id}')
    soup = BeautifulSoup(r.content, 'html.parser')
    spans = soup.find_all('span', {'class': 'current'})
    lines = [span.get_text() for span in spans]
    last_page_number = int(lines[0])

    print(f"Parsing {last_page_number} pages...")

    for page_num in range(1, last_page_number):
        r = SESSION.get(f'https://forum.toribash.com/tori_trans_hist.php?userid={user_id}&page={page_num}')
        soup = BeautifulSoup(r.content, 'html.parser')

        table = soup.find('table')
        list_table = tableDataText(table=table)

        for entry in list_table:
            for element in entry:
                if element in summer_categories:
                    total_volume += int(entry[2].replace(',', ''))
    
    print(f"Total TC spent in Summer Lottery 2023: {total_volume}TC")


def get_total_duel_profit(player):
    global user_id
    global profit
    global num_duels
    global total_volume

    profit = 0
    num_duels = 0
    total_volume = 0

    response = SESSION.get(f"https://forum.toribash.com/tori_stats.php?username={player}&format=json")
    user_stats = response.json()
    user_id = user_stats["userid"]

    print('ID:', user_id)

    r = SESSION.get(f'https://forum.toribash.com/tori_trans_hist.php?userid={user_id}')
    soup = BeautifulSoup(r.content, 'html.parser')
    spans = soup.find_all('span', {'class': 'current'})
    lines = [span.get_text() for span in spans]
    last_page_number = int(lines[0])

    print(f"Parsing {last_page_number} pages...")

    for page_num in range(1, last_page_number):
        r = SESSION.get(f'https://forum.toribash.com/tori_trans_hist.php?userid={user_id}&page={page_num}')
        soup = BeautifulSoup(r.content, 'html.parser')

        table = soup.find('table')
        list_table = tableDataText(table=table)

        for entry in list_table:
            for element in entry:
                if element == 'Duels':
                    if 'To' in entry[1]:
                        amount = -int(entry[2].replace(',', ''))
                    else:
                        amount = int(entry[2].replace(',', ''))

                    profit += amount
                    total_volume += abs(amount) / 2
                    num_duels += 1

    # Because duel amount is shown as double (user's tc wagered + opponent's tc wagered) we divide total profit by 2
    profit = profit / 2




def get_total_bets_profit(player):
    global user_id
    global profit
    global num_bets
    global gross_bet_amount

    profit = 0
    num_bets = 0
    gross_bet_amount = 0

    response = SESSION.get(f"https://forum.toribash.com/tori_stats.php?username={player}&format=json")
    user_stats = response.json()
    user_id = user_stats["userid"]

    print('ID:', user_id)

    r = SESSION.get(f'https://forum.toribash.com/tori_trans_hist.php?userid={user_id}')
    soup = BeautifulSoup(r.content, 'html.parser')
    spans = soup.find_all('span', {'class': 'current'})
    lines = [span.get_text() for span in spans]
    last_page_number = int(lines[0])

    print(f"Parsing {last_page_number} pages...")

    for page_num in range(1, last_page_number):
        r = SESSION.get(f'https://forum.toribash.com/tori_trans_hist.php?userid={user_id}&page={page_num}')
        soup = BeautifulSoup(r.content, 'html.parser')

        table = soup.find('table')
        list_table = tableDataText(table=table)

        for entry in list_table:
            for element in entry:
                if element == 'Bets':
                    # print(f"\nBet #{num_bets}:")

                    if 'To' in entry[1]:
                        amount = -int(entry[2].replace(',', ''))
                        # print(f"{entry[1]} - {-amount}")
                        gross_bet_amount += -amount

                        num_bets += 1
                    else:
                        amount = int(entry[2].replace(',', ''))
                        # print(f"Won {amount}TC")

                    profit += amount

    print(f"Profit: {profit}TC")
    print(f"Total bets placed: {num_bets}")
    print(f"Total TC bet: {gross_bet_amount}TC")


if __name__ == '__main__':
    player = Player(namespace.player)
    player.auth()

    start = time.time()

    print(f'Getting {namespace.action} information for {player.username}')

    match namespace.action:
        case 'bet':
            get_total_bets_profit(namespace.player)
        case 'duel':
            player.get_duel_profit()
        case 'summer-2023':
            summer_lottery(namespace.player)
        case _:
            exit(1)

    end = time.time()
    total_time = end - start
    total_time = datetime.timedelta(seconds=total_time)

    print(f'Script took: {total_time}')
