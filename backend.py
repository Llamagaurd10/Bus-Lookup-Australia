from fastapi import FastAPI

app = FastAPI()

@app.post("/lookup")
def lookup(data: PlateRequest, mode: str = "real"):
    plate = data.plate.strip()

    if mode == "silly":
        return random.choice(silly_database)

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

    # Return raw HTML for debugging
    return {"html": res.text}
