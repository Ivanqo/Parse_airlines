import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import time
from fake_useragent import UserAgent

def get_airport_coordinates(airport_name):
    """Получаем координаты аэропорта через поиск Google Maps"""
    try:
        # Генерируем случайный User-Agent
        ua = UserAgent()
        headers = {
            "User-Agent": ua.random,
            "Accept-Language": "en-US,en;q=0.9"
        }

        # Кодируем запрос
        query = urllib.parse.quote_plus(f"{airport_name} Airport")
        url = f"https://www.google.com/maps/search/{query}"
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Проверяем редирект на конкретное место
        if '@' in response.url:
            coords = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', response.url)
            if coords:
                return {
                    'latitude': float(coords.group(1)),
                    'longitude': float(coords.group(2)),
                    'source': 'Google Maps'
                }

        # Альтернативный парсинг из HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        meta = soup.find('meta', attrs={'property': 'og:image'})
        if meta:
            coords = re.search(r'center=(-?\d+\.\d+)%2C(-?\d+\.\d+)', meta['content'])
            if coords:
                return {
                    'latitude': float(coords.group(1)),
                    'longitude': float(coords.group(2)),
                    'source': 'Google Maps'
                }

        print(f"Координаты не найдены для {airport_name}")
        return None
        
    except Exception as e:
        print(f"Ошибка при поиске {airport_name}: {str(e)}")
        return None
    finally:
        time.sleep(3)  # Увеличенная задержка