import logging
from db_con import save_flight
import requests
import time
from datetime import datetime
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flight_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def setup_requests_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.flightradar24.com/",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://www.flightradar24.com",
        "DNT": "1",
        "Connection": "keep-alive"
    })
    return session

def fetch_flight_data(session, bounds):
    url = f"https://data-cloud.flightradar24.com/zones/fcgi/feed.js?bounds={bounds}&faa=1&satellite=1&mlat=1&flarm=1&adsb=1&gnd=1&air=1&vehicles=1&estimated=1&stats=1"
    try:
        response = session.get(url, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Ошибка получения данных: {str(e)}")
        return None

def process_flight(session, flight_id):
    url = f"https://data-live.flightradar24.com/clickhandler/?flight={flight_id}"
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.warning(f"Ошибка обработки рейса {flight_id}: {str(e)}")
        return None

def parse_timestamp(timestamp):
    try:
        return datetime.fromtimestamp(timestamp) if timestamp else None
    except:
        return None

def main():
    session = setup_requests_session()
    bounds = "48.0,40.0,26.0,44.0"  # Более широкий регион Чёрного моря
    
    while True:
        logging.info("Начало нового цикла мониторинга")
        
        try:
            # Получаем список рейсов
            data = fetch_flight_data(session, bounds)
            if not data:
                logging.warning("Нет данных от API")
                time.sleep(10)
                continue

            # Получаем список рейсов (исключаем системные поля)
            flights = {k: v for k, v in data.items() 
                      if k not in ['full_count', 'version', 'stats'] and isinstance(v, list)}
            
            if not flights:
                logging.warning("Нет данных о рейсах в ответе API")
                time.sleep(10)
                continue

            logging.info(f"Найдено {len(flights)} рейсов для обработки")

            # Обрабатываем каждый рейс
            for flight_id, flight_info in flights.items():
                try:
                    # Получаем детальную информацию о рейсе
                    detailed_data = process_flight(session, flight_id)
                    if not detailed_data:
                        continue

                    # Извлекаем данные
                    identification = detailed_data.get('identification', {})
                    aircraft = detailed_data.get('aircraft', {})
                    airport = detailed_data.get('airport')
                    if not airport:
                        logging.warning(f"Рейс {flight_id}: отсутствуют данные об аэропортах")
                        continue
                    
                    time_data = detailed_data.get('time', {})
                    status = detailed_data.get('status', {})

                    # Проверяем только обязательные поля (ICAO коды)
                    origin_icao = airport.get('origin', {}).get('code', {}).get('icao')
                    dest_icao = airport.get('destination', {}).get('code', {}).get('icao')
                    call_sign = identification.get('callsign')

                    if None in [origin_icao, dest_icao, call_sign]:
                        logging.warning(f"Пропуск рейса {flight_id} - отсутствуют обязательные ICAO коды или callsign")
                        continue
                    # Подготавливаем данные для сохранения (все остальные поля могут быть None)
                    flight_info = {
                        'call_sign': call_sign,
                        'icao_code': aircraft.get('registration'),
                        'model': aircraft.get('model', {}).get('text'),
                        'airline': detailed_data.get('airline', {}).get('name'),
                        'origin': {
                            'icao': origin_icao,
                            'iata': airport.get('origin', {}).get('code', {}).get('iata'),
                            'name': airport.get('origin', {}).get('name'),
                            'city': airport.get('origin', {}).get('position', {}).get('region', {}).get('city'),
                            'country': airport.get('origin', {}).get('position', {}).get('region', {}).get('country'),
                            'latitude': airport.get('origin', {}).get('position', {}).get('latitude'),
                            'longitude': airport.get('origin', {}).get('position', {}).get('longitude')
                        },
                        'destination': {
                            'icao': dest_icao,
                            'iata': airport.get('destination', {}).get('code', {}).get('iata'),
                            'name': airport.get('destination', {}).get('name'),
                            'city': airport.get('destination', {}).get('position', {}).get('region', {}).get('city'),
                            'country': airport.get('destination', {}).get('position', {}).get('region', {}).get('country'),
                            'latitude': airport.get('destination', {}).get('position', {}).get('latitude'),
                            'longitude': airport.get('destination', {}).get('position', {}).get('longitude')
                        },
                        'departure_time': parse_timestamp(time_data.get('real', {}).get('departure')),
                        'arrival_time': parse_timestamp(time_data.get('real', {}).get('arrival')),
                        'status': status.get('text')
                    }

                    # Логируем данные перед сохранением
                    logging.info(f"Попытка сохранения рейса: {flight_info['call_sign']}")

                    # Сохраняем рейс
                    if save_flight(
                        call_sign=flight_info['call_sign'],
                        icao_code=flight_info['icao_code'],
                        model=flight_info['model'],
                        airline_name=flight_info['airline'],
                        origin_data=flight_info['origin'],
                        destination_data=flight_info['destination'],
                        departure_time=flight_info['departure_time'],
                        arrival_time=flight_info['arrival_time'],
                        status=flight_info['status']
                    ):
                        logging.info(f"Рейс успешно сохранён: {flight_info['call_sign']}")
                    else:
                        logging.warning(f"Не удалось сохранить рейс: {flight_info['call_sign']}")

                except Exception as e:
                    logging.error(f"Ошибка обработки рейса {flight_id}: {str(e)}", exc_info=True)
                    continue

                time.sleep(5)  # Задержка между запросами

        except Exception as e:
            logging.critical(f"Критическая ошибка: {str(e)}", exc_info=True)
            time.sleep(300)
        finally:
            time.sleep(20)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Мониторинг остановлен")
    except Exception as e:
        logging.critical(f"Фатальная ошибка: {str(e)}", exc_info=True)