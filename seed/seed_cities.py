"""
این اسکریپت تمام فایل‌های CSV داخل پوشه Cities را می‌خواند و هر رکورد را
با ارسال ریکوئست به API مرحله دوم (POST /city) در دیتابیس Postgresql ذخیره می‌کند.

فرمت هر سطر CSV:  countyCode,city
مثال:              LT,Oklahoma City

اجرا:
    python seed/seed_cities.py
"""

import csv
import glob
import os
import time

import requests

API_URL = os.getenv("API_URL", "http://localhost:8000/city")
CITIES_DIR = os.getenv("CITIES_DIR", "Cities")


def wait_for_api(url: str, timeout: int = 60):
    """منتظر می‌ماند تا API بالا بیاید (برای زمانی که با docker-compose اجرا می‌شود)."""
    deadline = time.time() + timeout
    root_url = url.rsplit("/city", 1)[0] + "/docs"
    while time.time() < deadline:
        try:
            requests.get(root_url, timeout=2)
            return
        except requests.exceptions.RequestException:
            time.sleep(2)
    print("API در دسترس نشد، ادامه می‌دهیم به امید بهترین نتیجه...")


def seed():
    wait_for_api(API_URL)

    csv_files = glob.glob(os.path.join(CITIES_DIR, "*.csv"))
    if not csv_files:
        print(f"هیچ فایل CSV ای در '{CITIES_DIR}' پیدا نشد.")
        return

    total = 0
    for file_path in csv_files:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)  # رد کردن خط هدر (countyCode,city)

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
                    print(f"خطا برای {city}: {resp.status_code} - {resp.text}")

    print(f"تمام شد. {total} رکورد ارسال شد.")


if __name__ == "__main__":
    seed()
