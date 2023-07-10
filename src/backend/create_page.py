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
    with div(id="selectors",style="display:flex-horizontal;"):
        weapon_select = select(id="weapon-select",onchange="load()")
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
    br()
    with table(border=1,id="points-table"):
        thead(tr(th("Rank"),th("Name"),th("Country"),th("Points")))
        tbody(id="points-table-body")

    # script(type='text/javascript', src=Path("./src/scripts/index.js",).as_posix())
    script(type='text/javascript', src=Path("./dist/bundle.js").as_posix())

with open("index.html","w+") as page:
    page.write(doc.render())
