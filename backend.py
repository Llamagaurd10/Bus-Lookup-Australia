from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import random

app = FastAPI()

# Enable CORS so the frontend can access the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Request body format
class PlateRequest(BaseModel):
    plate: str

# Silly placeholder database
silly_database = [
    {
        "operator": "Ducklines Transport",
        "fleet_number": "🦆001",
        "chassis": "Bread-powered",
        "body": "Plastic pond bus",
        "notes": "Operated by quacking ducks"
    },
    {
        "operator": "ZoomBus Ltd.",
        "fleet_number": "ZB420",
        "chassis": "RocketFuel V12",
        "body": "Carbon fibre shell",
        "notes": "Faster than sound, breaks laws of physics"
    },
    {
        "operator": "Sleepy Express",
        "fleet_number": "NAP-777",
        "chassis": "SnoozeWagon",
        "body": "Mattress Deluxe",
        "notes": "Only departs during naps"
    }
]

@app.post("/lookup")
def lookup(data: PlateRequest, mode: str = "real"):
    plate = data.plate.strip()

    if mode == "silly":
        return random.choice(silly_database)

    # Otherwise, search the real site
    url = "https://fleetlists.busaustralia.com/index.php"
    form_data = {
        "searchtype": "numberplate",
        "searchstring": plate
    }

    try:
        response = requests.post(url, data=form_data, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return {"error": f"Failed to connect to fleetlists: {e}"}

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", class_="data")

    if not table:
        return {"error": "No results found."}

    rows = table.find_all("tr")
    if len(rows) < 2:
        return {"error": "No data rows found."}

    # Extract the first data row
    columns = rows[1].find_all("td")
    if len(columns) < 7:
        return {"error": "Unexpected table format."}

    return {
        "operator": columns[0].text.strip(),
        "fleet_number": columns[1].text.strip(),
        "chassis": columns[2].text.strip(),
        "body": columns[3].text.strip(),
        "notes": columns[6].text.strip()
    }
