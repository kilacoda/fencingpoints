from attrs import define
from bs4 import BeautifulSoup
import requests
from itertools import product
import sqlite3

conn = sqlite3.connect('fencers.db')
cursor = conn.cursor()

def get_points_value(points_str:list[str]):
    if len(points_str) == 0:
        return 0
    else:
        return float(points_str[0].strip(" ()"))

@define
class Fencer:
    rank: int
    name: str
    country: str
    points: dict[str, float]
    weapon: str
    gender: str
    category: str
    is_team: bool
fencers = []

for weapon,category,gender,event in product(
    ["S","F","E"],
    ['S','J'],
    ['M','W'],
    ['I','E']
):
    fencers_table = f"{weapon}_{category}_{gender}_{event}_fencers"
    event_results_table = f"{weapon}_{category}_{gender}_{event}_event_results"

    cursor.execute(
        f'''
        CREATE TABLE IF NOT EXISTS {fencers_table} (
            rank INTEGER PRIMARY KEY,
            name TEXT,
            country TEXT,
            points FLOAT
        );
        '''
    )
    cursor.execute(
        f'''
        DELETE FROM {fencers_table};
        '''
    )

    cursor.execute(
        f'''
        CREATE TABLE IF NOT EXISTS {event_results_table} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT,
            fencer_rank INTEGER,
            points_earned FLOAT
        );
        '''
    )
    cursor.execute(
        f'''
        DELETE FROM {event_results_table};
        '''
    )

    results_page = requests.get(f"https://fie.org/athletes/general-ranks/",dict(category=category,weapon=weapon,gender=gender,event=event,season=2023))
    print(results_page.url)

    soup = BeautifulSoup(results_page.content, 'html.parser')
    headers = soup.find_all("th",class_="GeneralRanks-header")
    events = [_event.contents[0].contents[0] for _event in headers[:-1]]

    all_fencers = soup.find_all("tr",class_="GeneralRanks-fencer")

    new_fencers = []
    is_team =  True if (event == "E") else False

    for fencer in all_fencers:
        rank = fencer.find("td",class_="GeneralRanks-fencerRank").contents[0]
        name:str = fencer.find("td",class_="GeneralRanks-fencerName").contents[0]
        country = fencer.find("td",class_="GeneralRanks-fencerCountry").contents[0]

        results = fencer.find_all("td",class_="GeneralRanks-fencerResult")
        points = [get_points_value(result.contents) for result in results]

        name = name.replace("'","''")
        country = country.replace("'","''")
        print(            f'''
            INSERT INTO {fencers_table} VALUES (
                {rank},\'{name}\',\'{country}\',{sum(points)}
            )
            '''
        )
        cursor.execute(
            f'''
            INSERT INTO {fencers_table} VALUES (
                {rank},\'{name}\',\'{country}\',{sum(points)}
            )
            '''
        )

        for event_name, points_earned in zip(events, points):
            cursor.execute(
                f'''
                INSERT INTO {event_results_table} (event_name, fencer_rank,points_earned) VALUES (
                    '{event_name}',{rank},{points_earned}
                );
                '''
            )
        # print(results[0].contents)
        conn.commit()
        new_fencers.append(Fencer(rank,name,country,dict(zip(events,points)),weapon,gender,category,is_team))

    print(len(new_fencers))
    fencers.extend(new_fencers)
