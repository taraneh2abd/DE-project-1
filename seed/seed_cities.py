
import csv
import glob
import os
import time

import requests

API_URL = os.getenv("API_URL", "http://localhost:8000/city")
CITIES_DIR = os.getenv("CITIES_DIR", "Cities")


def wait_for_api(url: str, timeout: int = 60):
    deadline = time.time() + timeout
    root_url = url.rsplit("/city", 1)[0] + "/docs"
    while time.time() < deadline:
        try:
            requests.get(root_url, timeout=2)
            return
        except requests.exceptions.RequestException:
            time.sleep(2)
    print("api not availabe")


def seed():
    wait_for_api(API_URL)

    csv_files = glob.glob(os.path.join(CITIES_DIR, "*.csv"))
    if not csv_files:
        print(f"no csv found in'{CITIES_DIR}' .")
        return

    total = 0
    for file_path in csv_files:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)  
            
            for row in reader:
                if not row or len(row) < 2:
                    continue

                country_code = row[0].strip()
                city = row[1].strip()

                if not city or not country_code:
                    continue

                resp = requests.post(API_URL, json={
                    "city": city,
                    "country_code": country_code,
                })

                if resp.status_code == 200:
                    total += 1
                else:
                    print(f"error for {city}: {resp.status_code} - {resp.text}")

    print(f" {total} total records have been send.")


if __name__ == "__main__":
    seed()
