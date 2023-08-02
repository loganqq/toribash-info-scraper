import os
import time
import json
import datetime
import argparse
import hashlib
import requests

from bs4 import BeautifulSoup

from tb.exceptions import TBAuthenticationError
from tb.args import namespace

from dotenv import load_dotenv
load_dotenv('N:\\tb-duel-scrape\\.env')


class Player:

    def __init__(self, username):
        self.username = username
        self.session = requests.session()

        self.duel_profit = 0
        self.num_duels = 0
        self.gross_tc_dueled = 0

        self.bet_profit = 0
        self.num_bets = 0
        self.gross_tc_bet = 0

        self.total_tc_spent_on_summer_2023_lottery = 0
        
        response = self.session.get(f"https://forum.toribash.com/tori_stats.php?username={self.username}&format=json")
        user_stats = response.json()
        self.user_id = user_stats["userid"]


    def auth(self):
        login_url = 'https://forum.toribash.com/tori_trans_hist.php'
        login_data = dict(
                username='wizard',
                password='',
                securitytoken="guest",
                vb_login_md5password=hashlib.md5(os.getenv('SECRET').encode('utf-8')).hexdigest(),
                vb_login_md5password_utf=hashlib.md5(os.getenv('SECRET').encode('utf-8')).hexdigest(),
                submit="Login"
            )
        
        try:
            self.session.post(login_url, login_data)

            print(f'User: {self.username}\tID: {self.user_id}')
        
        except Exception as err:
            
            raise TBAuthenticationError(f'{err}')


    def __str__(self):
        result = ''
        for k, v in vars(self).items():
            result += f'{k}:\t{v}\n'
        
        return result


    def get_duel_profit(self):

        last_page_number = get_last_page(self, self.session)

        print(f"Parsing {last_page_number} pages...")

        for page_num in range(1, last_page_number):
            r = self.session.get(f'https://forum.toribash.com/tori_trans_hist.php?userid={self.user_id}&page={page_num}')
            soup = BeautifulSoup(r.content, 'html.parser')

            table = soup.find('table')
            list_table = parse_table_data(table=table)

            for entry in list_table:
                for element in entry:
                    if element == 'Duels':
                        if 'To' in entry[1]:
                            amount = -int(entry[2].replace(',', ''))
                        else:
                            amount = int(entry[2].replace(',', ''))

                        self.duel_profit += amount
                        self.gross_tc_dueled += abs(amount) / 2
                        self.num_duels += 1

        # Because duel amount is shown as double (user's tc wagered + opponent's tc wagered) we divide total profit by 2
        self.duel_profit = self.duel_profit / 2

        # update_json(self)

        # print(f"Profit: {self.duel_profit} TC")
        # print(f"Total duels played: {self.num_duels}")
        # print(f"Total TC volume: {self.gross_tc_dueled} TC")

    
    def get_bet_profit(self):

        last_page_number = get_last_page(self, self.session)

        print(f"Parsing {last_page_number} pages...")

        for page_num in range(1, last_page_number):
            r = self.session.get(f'https://forum.toribash.com/tori_trans_hist.php?userid={self.user_id}&page={page_num}')
            soup = BeautifulSoup(r.content, 'html.parser')

            table = soup.find('table')
            list_table = parse_table_data(table=table)

            for entry in list_table:
                for element in entry:
                    if element == 'Bets':
                        # print(f"\nBet #{num_bets}:")

                        if 'To' in entry[1]:
                            amount = -int(entry[2].replace(',', ''))
                            # print(f"{entry[1]} - {-amount}")
                            self.gross_tc_bet += -amount

                            self.num_bets += 1
                        else:
                            amount = int(entry[2].replace(',', ''))
                            # print(f"Won {amount}TC")

                        self.bet_profit += amount
                    
        # update_json(self)

        # print(f"Profit: {self.bet_profit}TC")
        # print(f"Total bets placed: {self.num_bets}")
        # print(f"Total TC bet: {self.gross_tc_bet}TC")
    

    def get_summer_lottery_info(self):

        summer_categories = ['Summer Lottery 2023 - Epic Ticket', 'Summer Lottery 2023 - Mystery Ticket', 'Summer Lottery 2023 - 10 Cheap and Sunburnt Ticket', 'Summer Lottery 2023 - 10 Luxury Tickets (Discount)']

        last_page_number = get_last_page(self, self.session)

        print(f"Parsing {last_page_number} pages...")

        for page_num in range(1, last_page_number):
            r = self.session.get(f'https://forum.toribash.com/tori_trans_hist.php?userid={self.user_id}&page={page_num}')
            soup = BeautifulSoup(r.content, 'html.parser')

            table = soup.find('table')
            list_table = parse_table_data(table=table)

            for entry in list_table:
                for element in entry:
                    if element in summer_categories:
                        self.total_tc_spent_on_summer_2023_lottery += int(entry[2].replace(',', ''))
        
        # update_json(self)
        
        print(f"Total TC spent in Summer Lottery 2023: {self.total_tc_spent_on_summer_2023_lottery}TC")


def update_json(player: Player):
    with open('N:\\tb-duel-scrape\\player_info.json', 'r+') as file:
        data = json.load(file)
    
        if player.username not in data:
            data[player.username] = {}

        for key, value in vars(player).items():
            if key != 'username' and data[player.username].get(key) != value:
                data[player.username] = value
        
        file.seek(0)
        json.dump(data, file)
        file.truncate()


def get_last_page(player: Player, session: requests.Session) -> int:

    r = session.get(f'https://forum.toribash.com/tori_trans_hist.php?userid={player.user_id}')
    soup = BeautifulSoup(r.content, 'html.parser')
    spans = soup.find_all('span', {'class': 'current'})
    lines = [span.get_text() for span in spans]
    last_page_number = int(lines[0])

    return last_page_number


def parse_table_data(table):
    def _get_row_data(tr, col_tag='td'):
        return [td.get_text(strip=True) for td in tr.find_all(col_tag)]
    
    rows = []
    trs = table.find_all('tr')
    header_row = _get_row_data(trs[0], 'th')

    if header_row:
        rows.append(header_row)
        trs = trs[1:]
    
    for tr in trs:
        rows.append(_get_row_data(tr, 'td'))
    
    return rows
