CREATE DATABASE metabase_db;
GRANT ALL PRIVILEGES ON DATABASE metabase_db TO postgres;

-- Для таблицы airlines
ALTER TABLE airlines ADD CONSTRAINT airlines_icao_code_unique UNIQUE (icao_code);

-- Для таблицы airports
ALTER TABLE airports ADD CONSTRAINT airports_icao_code_unique UNIQUE (icao_code);

-- Создаем таблицу airports с координатами
CREATE TABLE airports (
    icao_code VARCHAR(4) PRIMARY KEY,
    iata_code VARCHAR(3),  -- Добавлен новый столбец
    name VARCHAR(100) NOT NULL,
    city VARCHAR(50),
    country VARCHAR(50),
    latitude DECIMAL(10, 6),
    longitude DECIMAL(10, 6)
);

-- Создаем таблицу airlines
CREATE TABLE airlines (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    icao_code VARCHAR(3)
);

-- Создаем таблицу flights
CREATE TABLE flights (
    id SERIAL PRIMARY KEY,
    call_sign VARCHAR(20),
    icao_code VARCHAR(10),
    model VARCHAR(20),
    airline_id INTEGER REFERENCES airlines(id),
    origin_airport VARCHAR(4) REFERENCES airports(icao_code),
    destination_airport VARCHAR(4) REFERENCES airports(icao_code),
    departure_time TIMESTAMP WITH TIME ZONE,
    arrival_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20)
);

-- Витрины
CREATE VIEW airline_stats AS
SELECT 
    a.name AS airline,
    COUNT(f.id) AS total_flights,
    AVG(EXTRACT(EPOCH FROM (f.arrival_time - f.departure_time)))/3600 AS avg_duration_hours,
    SUM(CASE WHEN f.status = 'Delayed' THEN 1 ELSE 0 END) AS delayed_flights
FROM flights f
JOIN airlines a ON f.airline_id = a.id
GROUP BY a.name;

CREATE VIEW top_airports AS
SELECT 
    ap.name AS airport,
    ap.city,
    COUNT(f.id) AS total_flights
FROM flights f
JOIN airports ap ON f.origin_airport = ap.icao_code OR f.destination_airport = ap.icao_code
GROUP BY ap.name, ap.city
ORDER BY total_flights DESC
LIMIT 10;

CREATE MATERIALIZED VIEW popular_routes AS
SELECT 
    o.name AS origin,
    d.name AS destination,
    o.latitude AS origin_lat,
    o.longitude AS origin_lon,
    d.latitude AS dest_lat,
    d.longitude AS dest_lon,
    COUNT(*) AS flights_count
FROM flights f
JOIN airports o ON f.origin_airport = o.icao_code
JOIN airports d ON f.destination_airport = d.icao_code
GROUP BY o.name, d.name, o.latitude, o.longitude, d.latitude, d.longitude
ORDER BY flights_count DESC
LIMIT 20;
