import dominate
from dominate.tags import *

import sqlite3
import json
from pathlib import Path

conn = sqlite3.connect("fencers.db")
cursor = conn.cursor()
with open("federations.json","r") as f:
    zones = json.load(f)
    print(zones)
doc = dominate.document(title="Fencing Points Tracker")
with doc.head:
    link(rel='stylesheet', href= Path("./src/styles/style.css").as_posix())

with doc:
    h1("Fencing Points Tracker")
    p("This page is meant to simplify looking up Olympic qualification standings for the 2024 Paris Olympics. You can select different options in the dropdowns below to get the table for a specific event.")
    p("The data is scraped from the", a("FIE website",href="https://fie.org/athletes"), ", and is updated whenever I make a change to the code or likely after a major event. If you want to see the code, or contribute, check out the Github repo: ",a("Source (GitHub)",href="https://github.com/kilacoda/fencing_points_tracker"))
    p(b("NOTE:")," Olympic qualification only counts events from April 3rd, 2023 - April 1st, 2024, hence the difference between the overall and Olympic standings.")
    p("Qualification legend:")
    with div(id="qualification-info"):
        div(style="width: 13pt; height: 13pt; background-color: green;border: 1px solid black;")
        p("Qualified (team/zone qualified individual)    ")
        div(style="width: 13pt; height: 13pt; background-color: gray;border: 1px solid black;")
        p("Qualified (individual qualified due to team)\t")
        div(style="width: 13pt; height: 13pt;border: 1px solid black;")
        p("Did not qualify")
    br()
    br()
    with div(id="selectors",style="display:flex-horizontal;"):
        weapon_select = select(id="weapon-select")
        with weapon_select:
            option("Sabre",value="S")
            option("Foil",value="F")
            option("Epee",value="E")

        gender_select = select(id="gender-select")
        with gender_select:
            option("Men",value="M")
            option("Women",value="W")

        event_select = select(id="event-select")
        with event_select:
            option("Individual",value="I")
            option("Team",value="E")

        category_select = select(id="category-select")
        with category_select:
            option("Senior",value="S")
            option("Junior",value="J")

        zone_select = select(id="zone-select")
        with zone_select:
            option("Worldwide",value="world")
            for zone in zones:
                option(zone,value=zone)

        points_type_select = select(id="points-type-select")
        with points_type_select:
            option("Olympic",value="olympic")
            option("Overall",value="overall")
    br()
    with table(border = 1,id="points-table"):
        thead(tr(th("Rank"),th("Name"),th("Country"),th("Points")))
        tbody(id="points-table-body")

    # script(type='text/javascript', src=Path("./src/scripts/index.js",).as_posix())
    script(type='text/javascript', src=Path("./dist/bundle.js").as_posix())

with open("index.html","w+") as page:
    page.write(doc.render())
