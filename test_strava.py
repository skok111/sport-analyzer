import requests
import os
import csv
import time
from dotenv import load_dotenv

# 1. Setup
load_dotenv()
CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
REFRESH_TOKEN = os.getenv('STRAVA_REFRESH_TOKEN')
nazwa_pliku = 'moje_treningi.csv'

def pobierz_token():
    auth_url = "https://www.strava.com/oauth/token"
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': REFRESH_TOKEN,
        'grant_type': 'refresh_token'
    }
    res = requests.post(auth_url, data=payload)
    return res.json().get('access_token')

# 2. Sprawdzamy "punkt startowy" (ostatni trening w CSV)
last_timestamp = 0
if os.path.isfile(nazwa_pliku):
    with open(nazwa_pliku, 'r', encoding='utf-8') as f:
        rows = list(csv.reader(f))
        if len(rows) > 1:
            # Szukamy ostatniego zapisanego treningu, by wyciągnąć jego datę (Unix Timestamp)
            # Uwaga: Strava API najlepiej filtruje po 'after' używając Epoch Timestamp
            # Na potrzeby tego skryptu uprościmy to: pobierzemy wszystko i odfiltrujemy ID
            last_ids = [row[0] for row in rows[1:]]
        else:
            last_ids = []
else:
    last_ids = []

token = pobierz_token()
headers = {"Authorization": f"Bearer {token}"}
url = "https://www.strava.com/api/v3/athlete/activities"

wszystkie_nowe = []
page = 1
pobieraj_dalej = True

print("🚀 Rozpoczynam inteligentną synchronizację...")

# 3. Pętla pobierająca STRONAMI (obsłuży nawet 10 000 treningów)
while pobieraj_dalej:
    print(f"📡 Pobieram stronę {page}...")
    params = {'per_page': 100, 'page': page}
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print("❌ Błąd API!")
        break
        
    batch = response.json()
    
    if not batch: # Jeśli strona jest pusta, znaczy że pobraliśmy wszystko
        break
        
    for t in batch:
        if str(t['id']) in last_ids:
            pobieraj_dalej = False # Znaleźliśmy trening, który już mamy - koniec!
            break
        wszystkie_nowe.append(t)
    
    if pobieraj_dalej:
        page += 1
        time.sleep(0.5) # Mała przerwa, żeby nie przeciążyć API (dobra praktyka)

# 4. Zapis chronologiczny
if wszystkie_nowe:
    wszystkie_nowe.reverse() # Najstarsze z nowych na górę
    plik_istnieje = os.path.isfile(nazwa_pliku)
    
    with open(nazwa_pliku, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not plik_istnieje:
            writer.writerow(['ID', 'Data', 'Nazwa', 'Dystans_km', 'Czas_min'])
        
        for t in wszystkie_nowe:
            data = t['start_date_local'][:10]
            dystans = round(t['distance'] / 1000, 2)
            czas = round(t['moving_time'] / 60, 2)
            writer.writerow([t['id'], data, t['name'], dystans, czas])
            print(f"✨ Zsynchronizowano: {data} - {t['name']}")

    print(f"\n✅ Gotowe! Dodano {len(wszystkie_nowe)} nowych treningów.")
else:
    print("\n✅ Wszystko aktualne. Brak nowych treningów do pobrania.")