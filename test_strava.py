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
CSV_FILE = 'my_workouts.csv'

def get_access_token():
    auth_url = "https://www.strava.com/oauth/token"
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': REFRESH_TOKEN,
        'grant_type': 'refresh_token'
    }
    response = requests.post(auth_url, data=payload)
    return response.json().get('access_token')

# 2. Check the "starting point" (last activity in CSV)
if os.path.isfile(CSV_FILE):
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        rows = list(csv.reader(f))
        if len(rows) > 1:
            # Extract IDs of already saved activities
            last_ids = [row[0] for row in rows[1:]]
        else:
            last_ids = []
else:
    last_ids = []

token = get_access_token()
headers = {"Authorization": f"Bearer {token}"}
url = "https://www.strava.com/api/v3/athlete/activities"

all_new_activities = []
page = 1
keep_fetching = True

print("🚀 Starting smart synchronization...")

# 3. Fetching loop (handles pagination)
while keep_fetching:
    print(f"📡 Fetching page {page}...")
    params = {'per_page': 100, 'page': page}
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print("❌ API Error!")
        break
        
    batch = response.json()
    
    if not batch: # If page is empty, we've fetched everything
        break
        
    for activity in batch:
        if str(activity['id']) in last_ids:
            keep_fetching = False # Found an activity we already have - stop!
            break
        all_new_activities.append(activity)
    
    if keep_fetching:
        page += 1
        time.sleep(0.5) # Small pause to avoid rate limits

# 4. Save chronologically
if all_new_activities:
    all_new_activities.reverse() # Oldest of the new on top
    file_exists = os.path.isfile(CSV_FILE)
    
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            # Added 'Type' column here!
            writer.writerow(['ID', 'Date', 'Name', 'Type', 'Distance_km', 'Duration_min'])
        
        for activity in all_new_activities:
            date = activity['start_date_local'][:10]
            activity_type = activity['type'] # Extracting the activity type
            distance_km = round(activity['distance'] / 1000, 2)
            duration_min = round(activity['moving_time'] / 60, 2)
            
            writer.writerow([activity['id'], date, activity['name'], activity_type, distance_km, duration_min])
            print(f"✨ Synced: {date} - [{activity_type}] {activity['name']}")

    print(f"\n✅ Done! Added {len(all_new_activities)} new activities.")
else:
    print("\n✅ Up to date. No new activities to fetch.")