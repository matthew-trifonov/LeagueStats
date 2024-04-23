import requests
from datetime import datetime, timedelta
import config

api_key1 = '?api_key=' + config.API_KEY_1
api_key2 = '?api_key=' + config.API_KEY_2
match_data_dict = {}

def get_data_analysis(winrate_criteria, userId):
    for match in match_data_dict:
        players = match_data_dict[match]['info']['participants']
        current_player = next(filter(lambda player: player['puuid'] == userId, players), None)      
        if winrate_criteria == 'game_length':
            get_time_winrate(current_player, match_data_dict[match])
        else:
            get_champ_winrate(winrate_criteria, current_player, players)
                
def set_match_data(urls):
    last_timestamp = None
    
    for url in urls:
        while True:
            req = requests.get(url)

            if req.status_code == 404:
                return last_timestamp
            
            if req.status_code != 429:
                r = req.json()
                match_data_dict[r['metadata']['matchId']] = r
                last_timestamp = r['info']['gameStartTimestamp']
                break
    return last_timestamp

def get_time_winrate(matching_player, r):
    isWin = matching_player['win']
    start = r['info']['gameStartTimestamp']
    end = r['info']['gameEndTimestamp']
    start_timestamp = datetime.fromtimestamp(start / 1000)
    end_timestamp = datetime.fromtimestamp(end / 1000)
    difference_seconds = (end_timestamp - start_timestamp).total_seconds()
    difference_minutes = difference_seconds / 60

    intervals = [15, 20, 25, 30, 35, 40, 45]
    for i, interval in enumerate(intervals):
        if difference_minutes < interval:
            key = f"{interval - 5} < {interval}" if interval > 15 else f"< {interval}"
            if key not in champ_dict:
                champ_dict[key] = {"wins": 0, "losses": 0}
            if isWin:
                champ_dict[key]["wins"] += 1
            else:
                champ_dict[key]["losses"] += 1
            return
    key = "> 45"
    if key not in champ_dict:
        champ_dict[key] = {"wins": 0, "losses": 0}
    if isWin:
        champ_dict[key]["wins"] += 1
    else:
        champ_dict[key]["losses"] += 1

def get_champ_winrate(winrate_criteria, current_player, players):
    current_team = current_player['teamId']

    for opponent in players:
        if opponent['teamId'] != current_team and winrate_criteria == 'enemies':
            champ = opponent['championName']
            isWin = opponent['win']
            if champ not in champ_dict:
                champ_dict[champ] = {'wins': 0, 'losses': 0}
            record = champ_dict[champ]
            if isWin:
                record["losses"] += 1
            else:
                record["wins"] += 1
        elif opponent['teamId'] == current_team and winrate_criteria == 'teammates':
            champ = opponent['championName']
            isWin = opponent['win']
            if champ not in champ_dict:
                champ_dict[champ] = {'wins': 0, 'losses': 0}
            record = champ_dict[champ]
            if isWin:
                record["wins"] += 1
            else:
                record["losses"] += 1

def get_matches(start_time, end_time, userId, winrate_criteria, type='ranked', queue=420, count=100):
    if not match_data_dict:
        matches = [1]
        while matches and len(matches) > 0:
            url = f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{userId}/ids{api_key1}'
            url += f'&startTime={start_time}&endTime={end_time}&queue={queue}&type={type}&count={10}'
            print(url)
            r = requests.get(url)
            matches= r.json()  
            api_keys = ['api_key1', 'api_key2']
            print(matches)
            #urls = [f'https://americas.api.riotgames.com/lol/match/v5/matches/{item}{api_keys[i % len(api_keys)]}' for i, item in matches]

            #print(urls)
            #timestamp = set_match_data(urls)
            if not timestamp:
                break
            end_time = int(timestamp / 1000)
    get_data_analysis(winrate_criteria, userId)
    
def get_data(name, winrate_criteria):
    url = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{name}{api_key2}'
    r = requests.get(url)
    print(r)
    userId = r.json().get('puuid')
    if not userId:
        return None
    current_datetime = datetime.now()
    one_year_ago = current_datetime - timedelta(days=385)
    start = int(one_year_ago.timestamp())
    end = int(current_datetime.timestamp())
    get_matches(userId=userId, start_time=start, end_time=end, winrate_criteria=winrate_criteria)

def get_stats(name, winrate_criteria):
    global champ_dict
    champ_dict = {}

    get_data(name, winrate_criteria)
    sorted_dict = sorted(champ_dict.items(), key=lambda x: (x[1]["wins"] / (x[1]["wins"] + x[1]["losses"])), reverse=True)
    return sorted_dict