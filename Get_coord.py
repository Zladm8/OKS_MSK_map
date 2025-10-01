### === GEOPY || Яндекс
from geopy.geocoders import Yandex
from geopy.exc import GeocoderUnavailable, GeocoderServiceError
import time

def is_valid_coordinates(lat, lon): # бывает чушь выдает
    if -90 <= lat <= 90 and -180 <= lon <= 180 and (lat, lon) != (0, 0):
        if lat != None:
            return True
        else:
            return False
    return False

def get_coordinates_yandex(address, max_retries=3, delay=0.2):
    api_key = "e55e8026-d709-428d-ab2b-b1c18d88d4bd"  # мой ключик
    geolocator = Yandex(api_key=api_key)

    for attempt in range(max_retries):
        try:
            location = geolocator.geocode(address, timeout=10)
            if location:
                lat, lon = location.latitude, location.longitude
                if is_valid_coordinates(lat, lon):
                    return [lat, lon]
                else:
                    # print(f"Некорректные координаты получены:")
                    pass  # Пробуем снова
            else:
                # print("Адрес не найден")
                pass

        except (GeocoderUnavailable, GeocoderServiceError) as e:
            # print(f"Ошибка сервиса: {e}")
            pass
        except Exception as e:
            # print(f"Неизвестная ошибка: {e}")
            pass

        if attempt < max_retries - 1:
            # print(f"Повторная попытка через {delay} секунд...")
            time.sleep(delay)

    return None