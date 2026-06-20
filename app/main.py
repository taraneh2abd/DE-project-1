import time

from fastapi import FastAPI

from app.core.db import Base, engine, SessionLocal
from app.core.redis import r, CACHE_TTL_SECONDS
from app.core.kafka import log_event
from app.models import City
from app.schemas import CitySchema

Base.metadata.create_all(bind=engine)

app = FastAPI()

LRU_TRACKER_KEY = "cache:lru_keys"
LRU_CAPACITY = 10

stats = {"hits": 0, "total": 0}


def cache_set(city: str, country_code: str):
    pipe = r.pipeline()
    pipe.set(city, country_code, ex=CACHE_TTL_SECONDS)

    pipe.lrem(LRU_TRACKER_KEY, 0, city)
    pipe.lpush(LRU_TRACKER_KEY, city)
    pipe.execute()

    size = r.llen(LRU_TRACKER_KEY)
    if size > LRU_CAPACITY:
        oldest = r.lrange(LRU_TRACKER_KEY, LRU_CAPACITY, -1)
        if oldest:
            r.ltrim(LRU_TRACKER_KEY, 0, LRU_CAPACITY - 1)
            for old_city in oldest:
                r.delete(old_city)


def cache_touch(city: str):
    r.expire(city, CACHE_TTL_SECONDS)
    r.lrem(LRU_TRACKER_KEY, 0, city)
    r.lpush(LRU_TRACKER_KEY, city)


@app.post("/city")
def create_or_update_city(data: CitySchema):
    db = SessionLocal()
    try:
        city = db.query(City).filter(City.city == data.city).first()

        if city:
            city.country_code = data.country_code
        else:
            city = City(city=data.city, country_code=data.country_code)
            db.add(city)

        db.commit()
        return {"status": "ok"}
    finally:
        db.close()


@app.get("/city/{city}")
def get_city(city: str):
    start = time.perf_counter()

    cached = r.get(city)
    stats["total"] += 1

    if cached is not None:
        stats["hits"] += 1
        cache_touch(city)

        elapsed_ms = (time.perf_counter() - start) * 1000
        hit_rate = (stats["hits"] / stats["total"]) * 100

        log_event({
            "response_time_ms": round(elapsed_ms, 3),
            "cache_status": "hit",
            "city": city,
            "cache_hit_rate_percent": round(hit_rate, 2),
        })

        return {"city": city, "country_code": cached, "source": "cache"}

    db = SessionLocal()
    try:
        result = db.query(City).filter(City.city == city).first()
    finally:
        db.close()

    elapsed_ms = (time.perf_counter() - start) * 1000
    hit_rate = (stats["hits"] / stats["total"]) * 100

    if not result:
        log_event({
            "response_time_ms": round(elapsed_ms, 3),
            "cache_status": "miss",
            "city": city,
            "cache_hit_rate_percent": round(hit_rate, 2),
            "found": False,
        })
        return {"error": "not found"}

    cache_set(city, result.country_code)

    log_event({
        "response_time_ms": round(elapsed_ms, 3),
        "cache_status": "miss",
        "city": city,
        "cache_hit_rate_percent": round(hit_rate, 2),
    })

    return {
        "city": city,
        "country_code": result.country_code,
        "source": "db",
    }
