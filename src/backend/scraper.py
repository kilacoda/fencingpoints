import datetime
from attrs import define
from bs4 import BeautifulSoup
import requests
from itertools import product
import sqlite3

conn = sqlite3.connect('fencers.db')
cursor = conn.cursor()

def get_points_value(points_str:list[str],olympic_exception=False):
    if len(points_str) == 0:
        return 0
    else:
        if "(" in points_str[0]:
            if olympic_exception:
                return float(points_str[0].strip('() '))
            return 0
        return float(points_str[0])

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

clear_db = True

for weapon,category,gender,event in product(
    ["S","F","E"],
    ['S','J'],
    ['M','W'],
    ['I','E']
):
    fencers_table = f"{weapon}_{category}_{gender}_{event}_fencers"
    event_results_table = f"{weapon}_{category}_{gender}_{event}_event_results"

    if clear_db:
        cursor.execute(
            f'''
            DROP TABLE IF EXISTS {fencers_table};
            '''
        )
        cursor.execute(
            f'''
            DROP TABLE IF EXISTS {event_results_table};
            '''
        )
    cursor.execute(
        f'''
        CREATE TABLE IF NOT EXISTS {fencers_table} (
            overall_rank INTEGER PRIMARY KEY,
            olympic_rank INTEGER,
            name TEXT,
            country TEXT,
            overall_points FLOAT,
            olympic_points FLOAT,
            olympic_qualified BOOLEAN DEFAULT(FALSE)
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
            fencer_overall_rank INTEGER,
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

    new_fencers = 0
    is_team =  True if (event == "E") else False

    for fencer in all_fencers:
        rank = fencer.find("td",class_="GeneralRanks-fencerRank").contents[0]
        name:str = fencer.find("td",class_="GeneralRanks-fencerName").contents[0]
        country = fencer.find("td",class_="GeneralRanks-fencerCountry").contents[0]

        results = fencer.find_all("td",class_="GeneralRanks-fencerResult")
        points = [result.contents for result in results[:-1]]

        name = name.replace("'","''")
        country = country.replace("'","''")
        # print(points)
        # print(f'''
        #     INSERT INTO {fencers_table} VALUES (
        #         {rank},\'{name}\',\'{country}\',{sum(points)}
        #     )
        #     '''
        # )
        olympic_points = 0

        for event_name, points_earned in zip(events, points):
            if category == "S":
                # print(repr(event_name[0:8]))
                event_date = datetime.datetime.strptime(event_name[0:8],"%d.%m.%y")
                if event_date > datetime.datetime(2023,4,1):
                    # print(f"Olympic event ==> {event_name}")
                    olympic_points += get_points_value(points_earned,olympic_exception=True)

            cursor.execute(
                f'''
                INSERT INTO {event_results_table} (event_name, fencer_overall_rank,points_earned) VALUES (
                    '{event_name}',{rank},{get_points_value(points_earned)}
                );
                '''
            )
        cursor.execute(
            f'''
            INSERT INTO {fencers_table} (overall_rank,name,country,overall_points,olympic_points) VALUES (
                {rank},\'{name}\',\'{country}\',{sum([get_points_value(p) for p in points])}, {olympic_points}
            )
            '''
        )

        new_fencers += 1

        # print(results[0].contents)

    query = f"""
    SELECT overall_rank, olympic_points FROM {fencers_table}
    ORDER BY olympic_points DESC;
    """
    print(query)
    ordered_ranks = list(enumerate(cursor.execute(query).fetchall()))
    for i, (ov_rank, oly_points) in ordered_ranks:
        query = f"""
        UPDATE {fencers_table}
        SET olympic_rank = {i + 1}
        WHERE overall_rank = {ov_rank};
        """
        cursor.execute(query)
    conn.commit()
    print(new_fencers)
    # fencers.extend(new_fencers)

