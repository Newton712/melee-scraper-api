from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import os
import shutil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # sécuriser plus tard si nécessaire
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def start_browser():
    # Vérifie si chromium est installé et détectable
    chrome_path = shutil.which("chromium") or shutil.which("google-chrome") or "/usr/bin/chromium"

    if not os.path.exists(chrome_path):
        raise RuntimeError("❌ Chromium non trouvé sur /usr/bin/chromium. Vérifie ton Dockerfile.")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.binary_location = chrome_path

    return webdriver.Chrome(options=options)

@app.get("/scrape")
def scrape(url: str = Query(...)):
    driver = start_browser()
    driver.get(url)

    tournament_id = url.split("/")[-1]
    tournament_name = driver.find_element(By.CSS_SELECTOR, "h3.mb-1").text.strip()
    raw_date = driver.find_element(By.CSS_SELECTOR, "span[data-toggle='datetime']").get_attribute("data-value").strip()
    dt = datetime.strptime(raw_date, "%m/%d/%Y %I:%M:%S %p") + timedelta(hours=2)
    formatted_date = dt.strftime("%d/%m/%Y %H:%M CEST")

    tournament = {
        "tournament_id": tournament_id,
        "tournament_name": tournament_name,
        "tournament_date": formatted_date,
    }

    players = set()
    elements = driver.find_elements(By.CSS_SELECTOR, 'a[data-type="player"]')
    for el in elements:
        name = el.get_attribute("innerHTML").split("<svg")[0].strip()
        if name:
            players.add(name)

    rows = driver.find_elements(By.CSS_SELECTOR, "#pairings tbody tr")
    tables = []
    for row in rows:
        try:
            table_num = row.find_element(By.CSS_SELECTOR, "td.TableNumber-column").text.strip()
            ps = row.find_elements(By.CSS_SELECTOR, 'a[data-type="player"]')
            p1 = ps[0].get_attribute("innerHTML").split("<svg")[0].strip()
            p2 = ps[1].get_attribute("innerHTML").split("<svg")[0].strip()
            tables.append({
                "round": "Ronde 1",
                "tableNum": table_num,
                "player_1": p1,
                "player_2": p2
            })
        except:
            continue

    driver.quit()

    return {
        "tournament": tournament,
        "players": sorted(players),
        "tables": tables
    }
