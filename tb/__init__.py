import os
import time
import datetime
import argparse
import hashlib
import requests

from bs4 import BeautifulSoup

from .exceptions import TBAuthenticationError

from dotenv import load_dotenv
load_dotenv('N:\\tb-duel-scrape\\.env')


class Player:

    def __init__(self, username):
        self.username = username

        self.session = requests.session()
        self.duel_profit = 0
        self.bet_profit = 0
        self.num_duels = 0
        self.num_bets = 0
        self.gross_tc_bet = 0
        self.gross_tc_dueled = 0

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


    def get_duel_profit(self):

        r = self.session.get(f'https://forum.toribash.com/tori_trans_hist.php?userid={self.user_id}')
        soup = BeautifulSoup(r.content, 'html.parser')
        spans = soup.find_all('span', {'class': 'current'})
        lines = [span.get_text() for span in spans]
        last_page_number = int(lines[0])

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

        print(f"Profit: {self.duel_profit} TC")
        print(f"Total duels played: {self.num_duels}")
        print(f"Total TC volume: {self.gross_tc_dueled} TC")


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
