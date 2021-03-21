from bs4 import BeautifulSoup
import re
import pandas as pd
from pathlib import Path
import urllib.request
import lxml
import datetime as dt
import sys
from time import sleep

data_file = Path("/Users/brian_miller/Data_Science/tennis_pipeline/match_data.xlsx")

if data_file.is_file():
    df = pd.read_excel(data_file).drop(columns=["Unnamed: 0"])
else:
    df = pd.DataFrame(columns=['date','winner','w_seed','loser','l_seed','score'])

yest = dt.date.today() - dt.timedelta(days=1)

yest_year = str(yest.year)
yest_month = str(yest.month)
if len(yest_month) == 1:
    yest_month = '0' + yest_month
yest_day = str(yest.day)
if len(yest_day) == 1:
    yest_day = '0' + yest_day

yest_string = yest_year + yest_month + yest_day

# allows the script to be run for any date by providing an arg
if len(sys.argv) > 1:
    yest_string = sys.argv[1]

link = "http://m.espn.com/general/tennis/dailyresults?date=" + yest_string
f = urllib.request.urlopen(link)

soup = BeautifulSoup(f, 'lxml')

tries = 1
while len(soup.find_all(string=re.compile("No Matches Scheduled", re.I))) > 0:
    if tries < 6:

        print('no matches, trying again')

        sleep(5)

        link = "http://m.espn.com/general/tennis/dailyresults?date=" + yest_string
        f = urllib.request.urlopen(link)

        soup = BeautifulSoup(f, 'lxml')

        tries += 1
    else:
        print('could\'t load matches, giving up\n')
        exit()

matches = soup.find_all('div', class_="boxscore-wrapper")

for m in matches:
    linescores = m.find_all('tr', class_='linescore')
    if 'winner' in linescores[0].get_attribute_list('class'):
        winner, loser = linescores
    else:
        loser, winner = linescores
    #winner = m.find('tr', class_='linescore winner')
    winner_and_seed = winner.find('td', class_='player-cell')
    winner_name = re.sub("\([0-9]+\) ", "", winner_and_seed.text)
    winner_seed = winner.find('span', class_='seed')
    if winner_seed != None:
        winner_seed = int(winner_seed.text.strip('( )'))
    else:
        winner_seed = "None"

    #loser = winner.find_next_sibling()
    loser_and_seed = loser.find('td', class_='player-cell')
    loser_name = re.sub("\([0-9]+\) ", "", loser_and_seed.text)
    loser_seed = loser.find('span', class_='seed')
    if loser_seed != None:
        loser_seed = int(loser_seed.text.strip('( )'))
    else:
        loser_seed = "None"

    num_sets = len(m.find_all('td', class_="set"))
    sets = zip(winner_and_seed.next_siblings, loser_and_seed.next_siblings)
    match_score = []
    for s in sets:
        set_score = s[0].text[0] + '-' + s[1].text[0]
        if len(s[0].text) > 1:
            tb_score = str(min(int(s[0].text[1:]), int(s[1].text[1:])))
            set_score += '(' + tb_score + ')'
        match_score.append(set_score)
    match_score = ' '.join(match_score)

    df = df.append({'date': yest_string,
                    'winner': winner_name,
                    'w_seed': winner_seed,
                    'loser': loser_name,
                    'l_seed':loser_seed,
                    'score': match_score},
                   ignore_index=True)

df.to_excel(data_file)
