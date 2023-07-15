from itertools import product
import sqlite3
import json
from pathlib import Path

conn = sqlite3.connect("fencers.db")
cursor = conn.cursor()

with open("federations.json","r") as f:
    feds = json.load(f)

for weapon,gender in product(
    ["S","F","E"],
    ['M','W']
):
    cursor.execute(f"""
                   UPDATE {weapon}_S_{gender}_E_fencers
                   SET olympic_qualified = TRUE
                   WHERE olympic_rank <= 4;
                   """)

    top_4 = cursor.execute(f"""
                           SELECT name FROM {weapon}_S_{gender}_E_fencers
                           WHERE olympic_rank <= 4;
                           """).fetchall()

    for fed in feds:
        # print(top_4)
        # print(feds[fed])
        for team in top_4:
            if team[0] in feds[fed]:
                feds[fed].remove(team[0])

        to_rep, rep_with = "\'", "\'\'"
        countries = [f"'{country.replace(to_rep,rep_with)}'" for country in feds[fed]]
        # print(','.join(countries))
        ranks_to_update = cursor.execute(f"""
            SELECT olympic_rank FROM {weapon}_S_{gender}_E_fencers
            WHERE (olympic_rank > 4) AND (name IN ({','.join(countries)}))
            LIMIT 1;
        """).fetchall()
        ranks_to_update = [str(_rank[0]) for _rank in ranks_to_update]
        print(ranks_to_update)
        print(f"""
                    UPDATE {weapon}_S_{gender}_E_fencers
                    SET olympic_qualified = TRUE
                    WHERE olympic_rank IN ({','.join(ranks_to_update)});
                    """)
        cursor.execute(f"""
                    UPDATE {weapon}_S_{gender}_E_fencers
                    SET olympic_qualified = TRUE
                    WHERE olympic_rank IN ({','.join(ranks_to_update)});
                    """)

        print(
            cursor.execute(f"""
                           SELECT * FROM {weapon}_S_{gender}_E_fencers
                           WHERE olympic_qualified = TRUE;
                           """).fetchall()
        )

conn.commit()


