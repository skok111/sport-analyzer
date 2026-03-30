import requests

# 1. Wklej tutaj swój ACCESS TOKEN (ten, który przed chwilą wyświetlił terminal)
ACCESS_TOKEN = '98033ece6a36dbfe241e6289592baef15057006e'

# 2. To jest specjalny adres Stravy (Endpoint) do pobierania listy treningów
url = "https://www.strava.com/api/v3/athlete/activities"

# 3. Pokazujemy wirtualną legitymację (dodajemy token do nagłówka zapytania)
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

print("Łączę się z bazą danych Stravy...")
# Tym razem używamy GET, bo chcemy POBRAĆ dane (wcześniej było POST)
response = requests.get(url, headers=headers)

# 4. Sprawdzamy odpowiedź serwera
if response.status_code == 200:
    treningi = response.json() # Przerabiamy odpowiedź na listę w Pythonie
    
    if len(treningi) > 0:
        ostatni_trening = treningi[0] # Bierzemy pierwszy z brzegu (najnowszy)
        
        # Wyciągamy interesujące nas dane (Strava podaje wszystko w metrach i sekundach)
        nazwa = ostatni_trening['name']
        dystans_m = ostatni_trening['distance']
        czas_s = ostatni_trening['moving_time']
        
        # Mała matematyka, żeby ładnie wyglądało
        dystans_km = round(dystans_m / 1000, 2)
        czas_min = round(czas_s / 60, 2)

        print("\n🏃 MAMY TO! Twój ostatni trening pobrany prosto z chmury:")
        print(f"👉 Tytuł: {nazwa}")
        print(f"👉 Dystans: {dystans_km} km")
        print(f"👉 Czas ruchu: {czas_min} min")
        print("\nGratulacje Inżynierze, ETAP 1 zakończony w 100%!")
    else:
        print("\nPołączyłem się ze Stravą, ale konto jest puste (nie ma treningów).")
else:
    print("\nUps, błąd połączenia! Czy token jest na pewno poprawny?")
    print(response.json())