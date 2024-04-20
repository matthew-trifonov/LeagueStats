import requests, json
import asyncio
import aiohttp
import time
from datetime import datetime, timedelta


champ_dict = {}
api_key = '?api_key=RGAPI-4f3c3b98-7570-46d8-a9c3-2e75390cd465'

def get_match_data(urls, userId, winrate_criteria):
    last_timestamp = None

    for url in urls:
        while True:

            req = requests.get(url)

            if req.status_code == 404:
                return last_timestamp
            
            if req.status_code != 429:
                
                r = req.json()  
                last_timestamp = r['info']['gameStartTimestamp']
                players = r['info']['participants']
                current_player = next(filter(lambda player: player['puuid'] == userId, players), None)
                current_team = current_player['teamId']
                if winrate_criteria == 'enemies':
                    enemy_team = list(filter(lambda player: player['teamId'] != current_team, players))
                    for opponent in enemy_team:
                        champ = opponent['championName'] 
                        isWin = opponent['win']

                        if champ not in champ_dict:
                            champ_dict[champ] = {'wins': 0, 'losses': 0}

                        record = champ_dict[champ]
                        if isWin:
                            record["losses"] += 1
                        else:
                            record["wins"] += 1
                elif  winrate_criteria == 'teamates': 
                    enemy_team = list(filter(lambda player: player['teamId'] == current_team, players))
                    for opponent in enemy_team:
                        champ = opponent['championName'] 
                        isWin = opponent['win']

                        if champ not in champ_dict:
                            champ_dict[champ] = {'wins': 0, 'losses': 0}

                        record = champ_dict[champ]
                        if isWin:
                            record["wins"] += 1
                        else:
                            record["losses"] += 1
                break
            time.sleep(10)
    return last_timestamp

def get_matches(start_time, end_time, userId, winrate_criteria, type='ranked', queue=420, count=100):
    matches = [1]
    while matches and len(matches) > 0:
        url = f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{userId}/ids{api_key}'
        url += f'&startTime={start_time}&endTime={end_time}&queue={queue}&type={type}&count={count}'
        r = requests.get(url)
        print(r)
        matches= r.json()  
        urls = [f'https://americas.api.riotgames.com/lol/match/v5/matches/{item}{api_key}' for item in matches]
        timestamp = get_match_data(urls, userId, winrate_criteria)
        if not timestamp:
            return
        end_time = int(timestamp / 1000)

def get_data(name, winrate_criteria):
    url = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{name}{api_key}'
    r = requests.get(url)
    print(r)
    userId = r.json()['puuid']
    if not userId:
        return None
    current_datetime = datetime.now()
    one_year_ago = current_datetime - timedelta(days=385)
    start = int(one_year_ago.timestamp())
    end = int(current_datetime.timestamp())
    get_matches(userId=userId, start_time=start, end_time=end, winrate_criteria = winrate_criteria)

def get_stats(name, winrate_criteria):
    get_data(name, winrate_criteria)
    sorted_champ_dict = sorted(champ_dict.items(), key=lambda x: (x[1]["wins"] / (x[1]["wins"] + x[1]["losses"])), reverse=True)
    return sorted_champ_dict


