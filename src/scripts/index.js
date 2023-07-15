import { createDbWorker } from "sql.js-httpvfs";

const federations = require("../../federations.json");

const workerUrl = new URL(
  "sql.js-httpvfs/dist/sqlite.worker.js",
  import.meta.url
);
const wasmUrl = new URL("sql.js-httpvfs/dist/sql-wasm.wasm", import.meta.url);

async function load(e) {
  const worker = await createDbWorker(
    [
      {
        from: "inline",
        config: {
          serverMode: "full",
          url: "../fencers.db",
          requestChunkSize: 4096,
        },
      },
    ],
    workerUrl.toString(),
    wasmUrl.toString()
  );
  console.log("worker", worker);
  const weapon = document.getElementById("weapon-select").value;
  const gender = document.getElementById("gender-select").value;
  const category = document.getElementById("category-select").value;
  const event = document.getElementById("event-select").value;
  const zone = document.getElementById("zone-select").value;
  const points_type = document.getElementById("points-type-select").value;

  console.log(weapon, gender, category, event, zone);
  var ranker = (points_type == 'overall') ? 'overall_rank' : 'olympic_rank';
  var points_to_use = (points_type == 'overall') ? 'overall_points' : 'olympic_points';

  if (zone == "world") {
    var query = `select * from ${weapon}_${category}_${gender}_${event}_fencers order by ${ranker} asc;`
  } else {
    var query = `select country from ${weapon}_${category}_${gender}_E_fencers where name in (${federations[zone].map((x) => `'${x.replace("'", "''")}'`).join(",")}) order by ${ranker} asc;`;

    console.log(query);
    const country_codes = await worker.db.query(query);

    console.log("country_codes", country_codes);
    query = `select * from ${weapon}_${category}_${gender}_${event}_fencers where country in (${country_codes.map((x) => `'${x["country"]}'`).join(",")}) order by ${ranker} asc;`;
  }

  console.log(query);
  const result = await worker.db.query(query);

  var points_table_body = document.getElementById("points-table-body");
  points_table_body.innerHTML = "";

  console.log(result);
  result.forEach((row) => {
    var backgroundColor = "none";
    var color = "black";
    if (points_type == "olympic") {
      if (event == "E") {
        console.log(row["olympic_qualified"]);
        if (row["olympic_qualified"] === 1) {
          console.log(`${row["name"]} is qualified`);
          backgroundColor = "green";
          color = "white";
        }
      }
    }
    var new_row = points_table_body.appendChild(document.createElement("tr"));

    var rank_cell = new_row.appendChild(document.createElement("td"));
    rank_cell.innerText = (category == "S") ? row[ranker] : row["overall_rank"];
    rank_cell.style.backgroundColor = backgroundColor;
    rank_cell.style.color = color;

    var name_cell = new_row.appendChild(document.createElement("td"));
    name_cell.innerText = row["name"];
    name_cell.style.backgroundColor = backgroundColor;
    name_cell.style.color = color;

    var country_cell = new_row.appendChild(document.createElement("td"));
    country_cell.innerText = row["country"];
    country_cell.style.backgroundColor = backgroundColor;
    country_cell.style.color = color;

    var points_cell = new_row.appendChild(document.createElement("td"));
    points_cell.innerText = (category == "S") ? row[points_to_use] : row["overall_points"];
    points_cell.style.backgroundColor = backgroundColor;
    points_cell.style.color = color;
  });
  // const result = await worker.db.query(`select * from E_S_M_I_fencers`);

}


load();

document.getElementById("weapon-select").addEventListener("change", load);
document.getElementById("gender-select").addEventListener("change", load);
document.getElementById("event-select").addEventListener("change", load);
document.getElementById("category-select").addEventListener("change", load);
document.getElementById("zone-select").addEventListener("change", load);
document.getElementById("points-type-select").addEventListener("change", load);
