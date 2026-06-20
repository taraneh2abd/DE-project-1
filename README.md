# DE-project-1

you can clear the DB and kafka and Redis as said below and also add the CSV to the DB from db-init.py script.

redis and kafka logs are triggered when a POST is recieved.

## how to run

```bash
docker compose up --build
docker compose up --no-build
```
document:  http://127.0.0.1:8000/docs#/

## create kafka topic

``docker exec -it kafka bash``

``/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list``

``/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic city_logs``

``/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic city_logs --partitions 1 --replication-factor 1``

``docker restart kafka``

## see logs in kafka

```docker exec -it cities_kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic city_logs --from-beginning```

- delete and create topice again to clear:

```docker exec -it cities_kafka kafka-topics --bootstrap-server localhost:9092 --delete --topic city_logs```

```docker exec -it cities_kafka kafka-topics --bootstrap-server localhost:9092 --create --topic city_logs --partitions 1 --replication-factor 1```

- for reseting the hint-rate:

```docker restart cities_app```

### Redis

``docker exec -it cities_redis redis-cli``

``keys *``

``MONITOR``

```DBSIZE```

```TTL tehran```

```docker exec -it cities_redis redis-cli FLUSHALL```

### Postgres

``docker exec -it cities_postgres psql -U user -d cities_db``
``\dt``

OR get into container then``psql -U user -d cities_db``
``\c cities``

``\d cities``
```SELECT * FROM cities limit 10;```

```SELECT COUNT(*) FROM cities;```
``TRUNCATE TABLE cities RESTART IDENTITY CASCADE;``


