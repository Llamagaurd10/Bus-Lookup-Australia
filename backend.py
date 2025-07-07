from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Allow any frontend to access this
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Request schema
class PlateRequest(BaseModel):
    plate: str

# Silly/fake results
silly_database = [
    {
        "operator": "Ducklines Transport",
        "fleet_number": "QUACK42",
        "chassis": "Toaster Wheels 9000",
        "body": "Rubber DuckShell",
        "notes": "Runs only on bread crusts"
    },
    {
        "operator": "Bogan Buses",
        "fleet_number": "42069",
        "chassis": "VB V8 Turbo",
        "body": "Falcon Shell",
        "notes": "Suspension made of footy socks"
    },
    {
        "operator": "Kinetic Meme Fleet",
        "fleet_number": "1337",
        "chassis": "Xbox Series X",
        "body": "RGB Gamer Bus",
        "notes": "Plays Darude Sandstorm on loop"
    }
]

@app.post("/lookup")
def lookup(data: PlateRequest, mode: str = "real"):
    plate = data.plate.strip()

    if mode == "silly":
        return random.choice(silly_database)

    # REAL scraping mode
    url = "https://fleetlists.busaustralia.com/index.php"
    form = {
        "searchtype": "numberplate",
        "searchstring": plate
    }

    try:
        res = requests.post(url, data=form, timeout=10)
        res.raise_for_status()
    except Exception as e:
        return {"error": f"Failed to connect to fleetlists: {e}"}

    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table", class_="data")
    if not table:
        return {"error": "No results found."}

    rows = table.find_all("tr")
    if len(rows) <= 1:
        return {"error": "No matching results found."}

    cols = [td.get_text(strip=True) for td in rows[1].find_all("td")]
    if len(cols) < 5:
        return {"error": "Data format unexpected."}

    return {
        "operator": cols[0],
        "fleet_number": cols[1],
        "chassis": cols[2],
        "body": cols[3],
        "notes": cols[4]
    }
