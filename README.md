# DE-project-1

## اجرا

فایل‌های CSV واقعی خودتان را داخل پوشه `Cities/` بریزید (همان فرمت `countyCode,city`)، سپس:

```bash
docker compose up --build
docker compose up --no-build
```

- run all dockers

``docker compose up -d``
``docker ps``

- fastapi
``uvicorn app.main:app --reload``

- create kafka topic
``docker exec -it kafka bash``
``/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list``
``/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic city_logs``
``/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic city_logs --partitions 1 --replication-factor 1``
``docker restart kafka``

see logs kafka
میتونی تاپیکو دیلیت کنی و دوباره بسازی
docker exec -it cities_kafka kafka-topics --bootstrap-server localhost:9092 --delete --topic city_logs
docker exec -it cities_kafka kafka-topics --bootstrap-server localhost:9092 --create --topic city_logs --partitions 1 --replication-factor 1
ریل تایم
docker exec -it cities_kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic city_logs --from-beginning
برای ریست شدن هیت ریت باید برنامه رو دوباره اجرا کنی چون توی رمه
docker restart cities_app

- Redis
``docker exec -it cities_redis redis-cli``
``keys *``
``MONITOR``
docker exec -it cities_redis redis-cli FLUSHALL

- Postgres
docker exec -it cities_postgres psql -U user -d cities_db
\dt
OR get into container then``psql -U user -d cities_db``
``\c cities``
\d cities
SELECT * FROM cities limit 10;
SELECT COUNT(*) FROM cities;
TRUNCATE TABLE cities RESTART IDENTITY CASCADE;


این کل ماجراست؛ هیچ batching یا تاخیری در کد نیست — به ازای هر ریکوئست بلافاصله یک پیام به کافکا push می‌شه چون producer.flush() صدا زده می‌شه که صف رو فوراً خالی می‌کنه و منتظر تایید broker می‌مونه.


## Redis size

docker exec -it cities_redis redis-cli
DBSIZE
KEYS *
TTL tehran : how many seconds to delete