""" This will have all of the functions that scrape from pro-football-reference.com """

import pandas as pd
from bs4 import BeautifulSoup
import requests
import numpy as np

def getBoxscoreData(boxscore_url):
    """
    - Takes in a url for a boxscore on pro-football-reference.com and outputs a list of data from that game.
        - The data is indexed by the boxscore url and includes:
            - Player summary statistics
            - Team summary statistics
            - Raw play by play data.
    """
    
    r = requests.get(boxscore_url)
    text = r.text.replace('<!--', '').replace('-->', '')
    soup = BeautifulSoup(text, 'lxml')

    player_df = pd.DataFrame(pd.read_html(str(soup.findAll(class_='overthrow table_container')[5]))[0])

    player_cols = player_df.columns.get_level_values(1)
    player_df = pd.DataFrame(player_df.values, columns=player_cols)
    player_df = player_df.rename(index=player_df.Player.astype(str)).drop(index=['nan', 'Player']).fillna(0).reset_index().drop(columns=['index'])
    player_df['boxscore'] = boxscore_url
    
    team_df = team_summary(soup, boxscore_url)
    PlayByPlay = rawPlayByPlay(soup, boxscore_url)
    
    return {boxscore_url : [player_df, team_df, PlayByPlay]}

def getCombineData(combine_url):
    
    r = requests.get(combine_url)
    text = r.text.replace('<!--', '').replace('-->', '')
    soup = BeautifulSoup(text, 'lxml')
    players = pd.read_html(str(soup.findAll(class_='table_outer_container')[0]))[0]
    
    return {combine_url: players}

def getBoxScoreUrls(year):
    """
    Takes in a year and returns all the boxscores for that year.
    """

    r = requests.get('https://www.pro-football-reference.com/years/' + str(year) + '/games.htm')
    text = r.text.replace('<!--', '').replace('-->', '')
    soup = BeautifulSoup(text, 'lxml')
    boxscores = []
    for url in soup.findAll(class_='overthrow table_container')[0].findAll('a'):
        if '/boxscores/' in str(url):
            boxscores.append('https://www.pro-football-reference.com' + str(url)[9:36])
    
    return list(set(boxscores))

def getCombineUrls(start_year, end_year):
    
    base_url = 'https://www.pro-football-reference.com/draft'
    
    years = end_year - start_year
    years_list = set([start_year + i for i in range(0, years)])
    
    combine_urls = []
    
    for year in years_list:
        year_url = base_url + '/' + str(year) + '-combine.htm'
        combine_urls.append(year_url)
    return combine_urls

def getCombineData(start_year, end_year):

    combine_data = []
    for d in getCombineUrls(start_year=start_year, end_year=end_year):
        combine_data.append(getCombineData(d))

    combine_df = list(combine_data[0].values())[0].append([list(combine_data[i+1].values())[0] for i in range(0, len(combine_data)-1)]).reset_index().drop(columns=['index'])

    return cleanCombineData(combine_df)

def cleanCombineData(combine_df):

    features = ['Height, Weight, age, salary, experience, combine stats, position, AV']
    combine_features = ['Ht', 'Wt', '40yd', 'Vertical','Bench', 'Broad Jump', '3Cone', 'Shuttle']

    def get_inches(x):
        try:
            return float(x[0]) * 12 + float(x[1])
        except:
            return float(0)
    combine_df['inches'] = combine_df[combine_features].Ht.str.replace('-', ' ').str.split(' ').apply(get_inches)

    to_floats = ['Wt', '40yd', 'Vertical','Bench', 'Broad Jump', '3Cone', 'Shuttle']

    def to_float_else_0(x):
        try:
            return float(x)
        except:
            return float(0)

    for col in to_floats:
        combine_df[col] = combine_df[col].apply(to_float_else_0)
    to_floats = ['Wt', '40yd', 'Vertical','Bench', 'Broad Jump', '3Cone', 'Shuttle']
    final_cols = list(set(to_floats + ['inches', 'Player', 'Pos', 'College', 'School', 'Drafted (tm/rnd/yr)', 'Ht']))

    combine_df = combine_df[final_cols]
    return combine_df

def team_summary(soup, boxscore_url):
    
    
    df = pd.DataFrame(pd.read_html(str(soup.findAll(class_='overthrow table_container')[4]))[0])
    cols = df.columns
    headers = df.T.iloc[0].values
    df = pd.DataFrame(df.T.values[1:], columns=headers)
    
    df['team'] = cols[1:]
    
    def get_index(lst, n):
        return lst[n]
    
    df['rush_atts'] = df['Rush-Yds-TDs'].str.split('-').apply(get_index, n=0)
    df['rush_yds'] = df['Rush-Yds-TDs'].str.split('-').apply(get_index, n=1)
    df['rush_tds'] = df['Rush-Yds-TDs'].str.split('-').apply(get_index, n=2)
    
    df['completions'] = df['Cmp-Att-Yd-TD-INT'].str.split('-').apply(get_index, n=0)
    df['pass_attempts'] = df['Cmp-Att-Yd-TD-INT'].str.split('-').apply(get_index, n=1)
    df['pass_yards'] = df['Cmp-Att-Yd-TD-INT'].str.split('-').apply(get_index, n=2)
    df['pass_tds'] = df['Cmp-Att-Yd-TD-INT'].str.split('-').apply(get_index, n=3)
    df['pass_int'] = df['Cmp-Att-Yd-TD-INT'].str.split('-').apply(get_index, n=4)
    
    df['times_sacked'] = df['Sacked-Yards'].str.split('-').apply(get_index, n=0)
    df['sacked_yards'] = df['Sacked-Yards'].str.split('-').apply(get_index, n=1)
    
    df['fumbles'] = df['Fumbles-Lost'].str.split('-').apply(get_index, n=0)
    df['fumbles_lost'] = df['Fumbles-Lost'].str.split('-').apply(get_index, n=1)
    
    df['penalties'] = df['Penalties-Yards'].str.split('-').apply(get_index, n=0)
    df['penalty_yards'] = df['Penalties-Yards'].str.split('-').apply(get_index, n=1)
    df['third_down_atts'] = df['Third Down Conv.'].str.split('-').apply(get_index, n=1)
    df['third_down_conv'] = df['Third Down Conv.'].str.split('-').apply(get_index, n=0)
    df['fourth_down_atts'] = df['Fourth Down Conv.'].str.split('-').apply(get_index, n=1)
    df['fourth_down_conv'] = df['Fourth Down Conv.'].str.split('-').apply(get_index, n=0)
    
    
    df['time_of_possession_seconds'] = ((df['Time of Possession'].str.split(':').apply(get_index, n=0).astype(float) * 60) +
                                         df['Time of Possession'].str.split(':').apply(get_index, n=1).astype(float))
    df['team_points'] = pd.DataFrame(pd.read_html(str(soup.findAll(class_='overthrow table_container')[0]))[0]).iloc[-1].values[-2:]
    df['opponent'] = df.team.values[::-1]
    
    df2 = pd.DataFrame(pd.read_html(str(soup.findAll(class_='overthrow table_container')[1]))[0])
    df2 = pd.DataFrame(df2.T.values[1:], columns=df2[0].tolist()).drop(columns=['Game Info'])
    for col in df2.columns:
        df[col] = [df2[col].values[0], df2[col].values[0]]
    
    try:
        df.Weather
    except:
        df['Weather'] = 'None'
    df = df.drop(columns=['Rush-Yds-TDs', 'Cmp-Att-Yd-TD-INT', 'Sacked-Yards', 'Fumbles-Lost',
                        'Penalties-Yards', 'Third Down Conv.', 'Fourth Down Conv.',
                        'Time of Possession'])
    
    for col in df.drop(columns=['Won Toss', 'Surface', 'opponent',
                                'Vegas Line', 'Over/Under', 'Roof', 'Weather']).columns:
        df['opponent_' + col] = df[col].values[::-1]
    
    
    
    df['date'] = soup.find(class_='scorebox_meta').findAll('div')[0].text
    df['time'] = soup.find(class_='scorebox_meta').findAll('div')[1].text
    df['stadium'] = soup.find(class_='scorebox_meta').findAll('div')[2].text[9:].strip()
    df['attendance'] = int(soup.find(class_='scorebox_meta').findAll('div')[3].text[12:].replace(',', ''))
    df['length_of_game_mins'] = length_of_game_mins = int(soup.find(class_='scorebox_meta').findAll('div')[4].text[14:][0])*60 + int(soup.find(class_='scorebox_meta').findAll('div')[4].text[14:][2:])
    
    
    for col in df.columns.drop('date'):
        df[col] = pd.to_numeric(df[col], errors='ignore')
    
    col_name_mapper = {}
    for col in df.columns:
        col_name_mapper[col] = col.replace(' ', '_').lower()
    
    df = df.rename(col_name_mapper, axis=1)
    
    df['win'] = (df.team_points > df.opponent_team_points)
    df['total'] = (df.team_points + df.opponent_team_points)
    df['over/under'] = df['over/under'].str[:4].astype(float)
    df['go_over?'] = (df.total > df['over/under'])
    df['wind'] = df.weather.str.split(',').apply(get_index, n=1).str[5:7].fillna(-1)
    df['temp'] = df.weather.str.split(',').apply(get_index, n=0).str[:2].fillna(-1)
    df['boxscore'] = boxscore_url
    
    return df

def clean_pass_rush_rec(boxscore_url):
    '''
    cleaning the pass rush rec table.
    '''
    
    r = requests.get('https://www.pro-football-reference.com/boxscores/201809090nwe.htm')
    text = r.text.replace('<!--', '').replace('-->', '')
    soup = BeautifulSoup(text, 'lxml')
    
    cols = df.columns.get_level_values(1)
    df = pd.DataFrame(df.values, columns=cols)
    
    return df.rename(index=df.Player.astype(str)).drop(index=['nan', 'Player']).fillna(0).reset_index().drop(columns=['index'])

def rawPlayByPlay(soup, boxscore_url):
    
    play_by_play = pd.DataFrame(pd.read_html(str(soup.findAll(class_='overthrow table_container')[19]))[0])
    play_by_play['boxscore'] = boxscore_url
    return play_by_play

