import csv
import glob
import os

import psycopg2

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "cities_db")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "pass")

CITIES_DIR = os.getenv("CITIES_DIR", "Cities")


def load_csv_rows(csv_path: str):
    """یک فایل CSV را می‌خواند و لیستی از (city, country_code) برمی‌گرداند."""
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)

        for row in reader:
            if not row or len(row) < 2:
                continue

            country_code = row[0].strip()
            city = row[1].strip()

            if not city or not country_code:
                continue

            rows.append((city, country_code))
    return rows


def main():
    csv_files = glob.glob(os.path.join(CITIES_DIR, "*.csv"))
    if not csv_files:
        print(f"هیچ فایل CSV ای در پوشه '{CITIES_DIR}' پیدا نشد.")
        return

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )
    conn.autocommit = False
    cur = conn.cursor()

    upsert_query = """
        INSERT INTO cities (city, country_code)
        VALUES (%s, %s)
        ON CONFLICT (city)
        DO UPDATE SET country_code = EXCLUDED.country_code;
    """

    total = 0
    try:
        for csv_path in csv_files:
            rows = load_csv_rows(csv_path)
            for city, country_code in rows:
                cur.execute(upsert_query, (city, country_code))
                total += 1
            print(f"{csv_path}: {len(rows)} رکورد پردازش شد.")

        conn.commit()
        print(f"\nتمام شد. مجموعاً {total} رکورد درج/آپدیت شد.")

    except Exception as e:
        conn.rollback()
        print(f"خطا رخ داد، تغییرات rollback شدند: {e}")
        raise

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()