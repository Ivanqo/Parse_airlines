import psycopg2
import logging
from psycopg2 import sql
from datetime import datetime
import os

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flight_tracker.log'),
        logging.StreamHandler()
    ]
)

def get_db_connection():
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "postgres"),
            database="flightdb",
            user="postgres",
            password="postgres",
            connect_timeout=5
        )
    except Exception as e:
        logging.error(f"Ошибка подключения к БД: {str(e)}")
        raise

def save_flight(call_sign, icao_code, model, airline_name, origin_data, destination_data, 
               departure_time=None, arrival_time=None, status=None):
    conn = None
    try:
        conn = get_db_connection()
        conn.autocommit = False
        cursor = conn.cursor()

        # 1. Упрощенное сохранение авиакомпании (без ON CONFLICT)
        if airline_name:
            cursor.execute(
                """
                INSERT INTO airlines (name, icao_code) 
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
                RETURNING id
                """,
                (airline_name, icao_code[:3] if icao_code else None)
            )
            airline_id = cursor.fetchone()[0] if cursor.rowcount > 0 else None
        else:
            airline_id = None

        # 2. Сохранение аэропортов с упрощенной логикой
        def save_airport(airport):
            if not airport or not airport.get('icao'):
                raise ValueError("Missing ICAO code")
            
            cursor.execute(
                """
                INSERT INTO airports (icao_code, iata_code, name, city, country)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (icao_code) DO NOTHING
                RETURNING icao_code
                """,
                (
                    airport['icao'],
                    airport.get('iata'),
                    airport.get('name'),
                    airport.get('city'),
                    airport.get('country')
                )
            )
            return cursor.fetchone()[0] if cursor.rowcount > 0 else airport['icao']

        try:
            origin_icao = save_airport(origin_data) if origin_data and origin_data.get('icao') else None
            dest_icao = save_airport(destination_data) if destination_data and destination_data.get('icao') else None
            
            if not origin_icao or not dest_icao:
                raise ValueError("Missing origin or destination ICAO codes")

        except Exception as e:
            logging.error(f"Ошибка сохранения аэропортов: {str(e)}")
            conn.rollback()
            return False

        # 3. Сохранение рейса
        cursor.execute("ALTER TABLE flights ADD COLUMN IF NOT EXISTS model TEXT;")
        cursor.execute(
            """
            INSERT INTO flights (
                call_sign, origin_airport, destination_airport,
                icao_code, airline_id, model,
                departure_time, arrival_time, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (
                call_sign,
                origin_icao,
                dest_icao,
                icao_code,
                airline_id,
                model,
                departure_time,
                arrival_time,
                status
            )
        )

        conn.commit()
        logging.info(f"Рейс сохранён: {call_sign}")
        return True

    except Exception as e:
        logging.error(f"Ошибка сохранения рейса: {str(e)}", exc_info=True)
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()