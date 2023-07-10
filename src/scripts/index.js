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
  const weapon = document.getElementById("weapon-select").value;
  const gender = document.getElementById("gender-select").value;
  const category = document.getElementById("category-select").value;
  const event = document.getElementById("event-select").value;
  const zone = document.getElementById("zone-select").value;

  console.log(weapon, gender, category, event, zone);

  if (zone == "world") {
    var query = `select * from ${weapon}_${category}_${gender}_${event}_fencers`
  } else {
    var query = `select country from ${weapon}_${category}_${gender}_E_fencers where name in (${federations[zone].map((x) => `'${x.replace("'", "''")}'`).join(",")});`;

    console.log(query);
    const country_codes = await worker.db.query(query);

    console.log("country_codes", country_codes);
    query = `select * from ${weapon}_${category}_${gender}_${event}_fencers where country in (${country_codes.map((x) => `'${x["country"]}'`).join(",")});`;
  }

  console.log(query);
  const result = await worker.db.query(query);

  var points_table_body = document.getElementById("points-table-body");
  points_table_body.innerHTML = "";

  console.log(result);
  result.forEach((row) => {
    var new_row = points_table_body.appendChild(document.createElement("tr"));
    new_row.appendChild(document.createElement("td")).innerText = row["rank"];
    new_row.appendChild(document.createElement("td")).innerText = row["name"];
    new_row.appendChild(document.createElement("td")).innerText = row["country"];
    new_row.appendChild(document.createElement("td")).innerText = row["points"];
  });
  // const result = await worker.db.query(`select * from E_S_M_I_fencers`);

}


load();

document.getElementById("weapon-select").addEventListener("change", load);
document.getElementById("gender-select").addEventListener("change", load);
document.getElementById("event-select").addEventListener("change", load);
document.getElementById("category-select").addEventListener("change", load);
document.getElementById("zone-select").addEventListener("change", load);
