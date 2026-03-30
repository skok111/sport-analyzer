import requests
import os
from dotenv import load_dotenv

# 1. Wczytujemy tajny sejf
load_dotenv()
CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
REFRESH_TOKEN = os.getenv('STRAVA_REFRESH_TOKEN')

print(f"Sejf wczytany! Client ID: {CLIENT_ID}")
print("🔄 Wyrabiam nowy bilet dostępu...")

# 2. Odświeżanie tokenu (magia, dzięki której kod działa zawsze)
auth_url = "https://www.strava.com/oauth/token"
auth_payload = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'refresh_token': REFRESH_TOKEN,
    'grant_type': 'refresh_token'
}

auth_response = requests.post(auth_url, data=auth_payload)

if auth_response.status_code == 200:
    nowy_access_token = auth_response.json()['access_token']
    print("✅ Nowy bilet wygenerowany! Pobieram dane...\n")
    
    # 3. Pobieranie treningów z NOWYM biletem
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {nowy_access_token}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        treningi = response.json()
        if len(treningi) > 0:
            ostatni_trening = treningi[0]
            nazwa = ostatni_trening['name']
            dystans_km = round(ostatni_trening['distance'] / 1000, 2)
            czas_min = round(ostatni_trening['moving_time'] / 60, 2)

            print("🏃 MAMY TO! Twój ostatni trening:")
            print(f"👉 Tytuł: {nazwa}")
            print(f"👉 Dystans: {dystans_km} km")
            print(f"👉 Czas ruchu: {czas_min} min")
            print("\nPełen sukces! Ten kod jest kuloodporny i nie wygaśnie.")
        else:
            print("Konto puste, brak treningów.")
    else:
        print("Błąd pobierania danych z API.")
else:
    print("Błąd odświeżania tokenu. Sprawdź plik .env!")