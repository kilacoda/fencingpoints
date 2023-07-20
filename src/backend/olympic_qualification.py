from itertools import product
from pprint import pprint
import sqlite3
import json
from pathlib import Path

conn = sqlite3.connect("fencers.db")
cursor = conn.cursor()


for weapon, gender in product(["S", "F", "E"], ["M", "W"]):
    with open("federations.json", "r") as f:
        feds = json.load(f)
    print()
    print(f"=== {weapon=} {gender=} ===")
    cursor.execute(
        f"""
                   UPDATE {weapon}_S_{gender}_E_fencers
                   SET olympic_qualified = TRUE
                   WHERE olympic_rank <= 4;
                   """
    )

    top_4 = cursor.execute(
        f"""
                           SELECT name FROM {weapon}_S_{gender}_E_fencers
                           WHERE olympic_rank <= 4;
                           """
    ).fetchall()

    print(f"===> Top 4: {top_4}")

    for fed in feds:
        # print(top_4)
        # print(feds[fed])
        for team in top_4:
            if team[0] in feds[fed]:
                feds[fed].remove(team[0])
                print(
                    f"===> {team[0]} already qualified. Removed {team[0]} from {fed} countries of consideration."
                )
        to_rep, rep_with = "'", "''"
        countries = [f"'{country.replace(to_rep,rep_with)}'" for country in feds[fed]]
        print(f"===> {countries=}")
        # print(','.join(countries))
        query = f"""
            SELECT olympic_rank FROM {weapon}_S_{gender}_E_fencers
            WHERE (olympic_rank > 4) AND (olympic_rank <= 16) AND (name IN ({','.join(countries)}))
            ORDER BY olympic_rank ASC
            LIMIT 1;
        """
        print(query)
        ranks_to_update = cursor.execute(query).fetchall()
        if len(ranks_to_update) == 0:
            query = f"""
                SELECT olympic_rank from {weapon}_S_{gender}_E_fencers
                WHERE olympic_qualified = FALSE
                ORDER BY olympic_rank ASC;
            """

            rank_to_qualify = cursor.execute(query).fetchall()
            ranks_to_update.append(min(rank_to_qualify))

            print(
                f"===> No country from {fed} qualified. Qualifying {ranks_to_update[0]}"
            )

        ranks_to_update = [str(_rank[0]) for _rank in ranks_to_update]
        print(f"===> {ranks_to_update=}")
        query = f"""
                    UPDATE {weapon}_S_{gender}_E_fencers
                    SET olympic_qualified = TRUE
                    WHERE olympic_rank IN ({','.join(ranks_to_update)});
                    """
        print(query)
        cursor.execute(query)

    query = f"""
        SELECT ind_fencers.olympic_rank, ind_fencers.name, team_fencers.country, team_fencers.olympic_qualified FROM {weapon}_S_{gender}_I_fencers AS ind_fencers
        INNER JOIN {weapon}_S_{gender}_E_fencers AS team_fencers
        ON ind_fencers.country = team_fencers.country
        ORDER BY ind_fencers.olympic_rank ASC;
        """

    print(query)

    cursor.execute(query)

    fencers = cursor.fetchall()

    query = f"""
        ALTER TABLE {weapon}_S_{gender}_I_fencers
        ADD qualified_by_team BOOLEAN DEFAULT(FALSE);
    """
    try:
        cursor.execute(query)
    except sqlite3.OperationalError:
        print("Column already exists")

    # pprint(fencers)
    query = f"""
        UPDATE {weapon}_S_{gender}_I_fencers
        SET olympic_qualified = TRUE, qualified_by_team = TRUE
        WHERE country IN (SELECT country FROM {weapon}_S_{gender}_E_fencers teams WHERE teams.olympic_qualified = TRUE)
    """
    print(query)
    cursor.execute(query)

    with open("federations.json", "r") as f:
        feds = json.load(f)
    print()
    with open("ioc_countries.json", "r") as f:
        ioc_countries = json.load(f)

    for fed in feds:
        if fed in ["Europe","Asia And Oceania"]:
            limit = 2
        else:
            limit = 1

        codes = [f"'{ioc_countries[country.lower().title()]}'" for country in feds[fed] if country.lower().title() in ioc_countries]

        if fed == "Europe":
            codes.append("'TUR'")
            codes.append("'GBR'")

        query = f"""
            SELECT olympic_rank
            FROM {weapon}_S_{gender}_I_fencers
            WHERE (country NOT IN (SELECT country FROM {weapon}_S_{gender}_E_fencers teams WHERE teams.olympic_qualified = TRUE)) AND (country IN ({','.join(codes)}))
            ORDER BY olympic_rank ASC
            LIMIT {limit};
        """
        print(query)
        ranks_to_update = cursor.execute(query).fetchall()

        query = f"""
            UPDATE {weapon}_S_{gender}_I_fencers
            SET olympic_qualified = TRUE, qualified_by_team = FALSE
            WHERE olympic_rank IN ({','.join([str(_rank[0]) for _rank in ranks_to_update])});
        """
        print(query)
        cursor.execute(query)

    qualified_countries = cursor.execute(
        f"""
            SELECT name FROM {weapon}_S_{gender}_E_fencers
            WHERE olympic_qualified = TRUE;
        """
    ).fetchall()
    qualified_countries = [country[0] for country in qualified_countries]
    pprint(qualified_countries)

    query = f"""
        SELECT olympic_rank, name
        FROM {weapon}_S_{gender}_I_fencers
        WHERE olympic_qualified = 1
        ORDER BY olympic_rank ASC;
    """
    cursor.execute(query)
    # pprint(cursor.fetchall())
    conn.commit()
