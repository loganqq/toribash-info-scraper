import argparse

parser = argparse.ArgumentParser()


parser.add_argument(
    'action',
    type=str,
    choices=['bet', 'duel', 'summer_2023'],
    help='Information that the script will fetch'
)

parser.add_argument(
    'player',
    nargs='+',
    help='The player(s) for which to get information for'
)


namespace = parser.parse_args()
