import streamlit as st
import pandas as pd
import altair as alt
import os
import json
import requests

# 1. Konfiguracja Strony
st.set_page_config(page_title="Sport Analyzer", page_icon="🏆", layout="centered")

# --- FUNKCJE POMOCNICZE DO USTAWIEŃ (PAMIĘĆ MIASTA) ---
SETTINGS_FILE = 'settings.json'

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {'city': None}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

# --- FUNKCJA DO POBIERANIA POGODY (Open-Meteo API) ---
def get_weather(city_name):
    try:
        # 1. Szukamy współrzędnych miasta (Geocoding API)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
        geo_resp = requests.get(geo_url).json()
        
        if "results" not in geo_resp or not geo_resp["results"]:
            return None, "City not found. Try a different name."
            
        lat = geo_resp["results"][0]["latitude"]
        lon = geo_resp["results"][0]["longitude"]
        resolved_city = geo_resp["results"][0]["name"]
        
        # 2. Pobieramy pogodę dla tych współrzędnych (dodaliśmy hourly=precipitation_probability)
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m&hourly=precipitation_probability&wind_speed_unit=kmh"
        w_resp = requests.get(weather_url).json()
        current = w_resp["current"]
        hourly = w_resp["hourly"]
        
        # Szukamy aktualnej godziny na liście, aby pobrać właściwe prawdopodobieństwo opadów
        try:
            current_time = current["time"]
            current_hour = current_time[:13] + ":00" 
            time_idx = hourly["time"].index(current_hour)
            chance_of_rain = hourly["precipitation_probability"][time_idx]
        except ValueError:
            chance_of_rain = 0
        
        return {
            "name": resolved_city,
            "temp": current["temperature_2m"],
            "feels_like": current["apparent_temperature"],
            "wind": current["wind_speed_10m"],
            "precip_prob": chance_of_rain, # Zmieniona zmienna
            "humidity": current["relative_humidity_2m"]
        }, None
    except Exception as e:
        return None, "Error connecting to weather service."

# 2. Inicjalizacja pamięci sesji (do nawigacji)
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'Home'

def go_to_view(view_name):
    st.session_state.current_view = view_name

# Funkcja: Ładne formatowanie tempa
def format_pace(decimal_pace):
    if pd.isna(decimal_pace) or decimal_pace <= 0 or decimal_pace > 100:
        return "-:--"
    mins = int(decimal_pace)
    secs = int(round((decimal_pace - mins) * 60))
    return f"{mins}:{secs:02d}"

# 3. Wczytanie danych i ustawień
user_settings = load_settings()

try:
    df = pd.read_csv('my_workouts.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Pace_min_km'] = df.apply(lambda row: row['Duration_min'] / row['Distance_km'] if row['Distance_km'] > 0 else 0, axis=1)
    total_runs = len(df[df['Type'] == 'Run'])
    total_rides = len(df[df['Type'] == 'Ride']) 
except FileNotFoundError:
    df = pd.DataFrame() 
    total_runs = 0
    total_rides = 0

# ==========================================
# 🏠 EKRAN GŁÓWNY: KOMPAKTOWA SIATKA 3x2
# ==========================================
if st.session_state.current_view == 'Home':
    
    st.markdown("""
    <style>
        span[class^="css-hook"] { display: none; }

        .welcome-bar {
            background: linear-gradient(to right, #1E1E1E, #2A2A2A);
            padding: 20px 30px; 
            color: white; 
            margin-bottom: 20px;
            border-radius: 12px;
            border-left: 6px solid #2D89EF;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        /* BAZOWY STYL DLA WSZYSTKICH PRZYCISKÓW: RÓWNE KWADRATY */
        div.stButton > button {
            aspect-ratio: 1 / 1 !important; 
            height: auto !important; 
            border-radius: 15px !important; 
            border: none !important;
            color: white !important;
            text-transform: uppercase !important;
            font-weight: 800 !important;
            letter-spacing: 0.5px !important;
            transition: all 0.2s ease-in-out !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            white-space: pre-wrap !important; 
            text-align: center !important;
            line-height: 1.4 !important;
            font-size: 1.1em !important;
        }

        div.stButton > button p { color: white !important; font-size: inherit !important; }

        div.stButton > button:hover {
            transform: translateY(-4px) !important;
            box-shadow: 0 8px 15px rgba(0,0,0,0.3) !important;
            filter: brightness(1.1) !important;
        }

        /* --- KOLORY --- */
        div[data-testid="stElementContainer"]:has(.css-hook-run) + div[data-testid="stElementContainer"] button {
            background: linear-gradient(135deg, #2D89EF 0%, #1a5b9e 100%) !important;
        }
        div[data-testid="stElementContainer"]:has(.css-hook-bike) + div[data-testid="stElementContainer"] button {
            background: linear-gradient(135deg, #00A300 0%, #006b00 100%) !important;
        }
        div[data-testid="stElementContainer"]:has(.css-hook-weather) + div[data-testid="stElementContainer"] button {
            background: linear-gradient(135deg, #00ABA9 0%, #00706f 100%) !important;
        }
        div[data-testid="stElementContainer"]:has(.css-hook-rec) + div[data-testid="stElementContainer"] button {
            background: linear-gradient(135deg, #F39C12 0%, #bd790e 100%) !important;
        }
        div[data-testid="stElementContainer"]:has(.css-hook-set) + div[data-testid="stElementContainer"] button {
            background: linear-gradient(135deg, #9B59B6 0%, #6c3e7f 100%) !important;
        }
        div[data-testid="stElementContainer"]:has(.css-hook-sync) + div[data-testid="stElementContainer"] button {
            background: linear-gradient(135deg, #E74C3C 0%, #a6362a 100%) !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="welcome-bar">
            <h1 style='margin: 0; font-size: 32px;'>Welcome back, Kacper!</h1>
            <p style='margin: 0; opacity: 0.8; font-size: 16px;'>Your Personal Sport Analyzer Center</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<span class="css-hook-run"></span>', unsafe_allow_html=True)
        if st.button(f"RUNNING\n\nTotal: {total_runs}", key="btn_run", use_container_width=True):
            go_to_view('Run')
            st.rerun()

    with col2:
        st.markdown('<span class="css-hook-bike"></span>', unsafe_allow_html=True)
        if st.button(f"CYCLING\n\nTotal: {total_rides}", key="btn_ride", use_container_width=True):
            go_to_view('Ride')
            st.rerun()
            
    with col3:
        st.markdown('<span class="css-hook-weather"></span>', unsafe_allow_html=True)
        # Zmieniamy napis na przycisku na zapisane miasto, lub "Setup" jeśli brak
        city_display = user_settings.get('city')
        btn_text = f"WEATHER\n{city_display}" if city_display else "🌤️ WEATHER\nSetup City"
        
        if st.button(btn_text, key="btn_weather", use_container_width=True):
            go_to_view('Weather')
            st.rerun()

    st.write("") 

    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown('<span class="css-hook-rec"></span>', unsafe_allow_html=True)
        if st.button("RECORDS\n\nPersonal bests", key="btn_rec", use_container_width=True):
            go_to_view('Records')
            st.rerun()

    with col5:
        st.markdown('<span class="css-hook-set"></span>', unsafe_allow_html=True)
        if st.button("⚙️ SETTINGS", key="btn_settings", use_container_width=True):
            st.toast("Settings clicked! ⚙️")

    with col6:
        st.markdown('<span class="css-hook-sync"></span>', unsafe_allow_html=True)
        if st.button("🔄 STRAVA SYNC\nFetch data", key="btn_sync", use_container_width=True):
            st.toast("Syncing with Strava... 🔄")

    # === DASHBOARD ===
    st.divider()
    st.markdown("### 📈 Overall Progress")
    
    if not df.empty and 'Type' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        
        def format_duration(total_min):
            h = int(total_min // 60)
            m = int(total_min % 60)
            s = int((total_min * 60) % 60)
            return f"{h:02d}:{m:02d}:{s:02d}"

        st.markdown("#### 📊 All-Time Stats")
        total_workouts = len(df)
        total_time_min = df['Duration_min'].sum()
        run_dist = df[df['Type'] == 'Run']['Distance_km'].sum()
        ride_dist = df[df['Type'] == 'Ride']['Distance_km'].sum()
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Workouts", total_workouts)
        c2.metric("Total Active Time", format_duration(total_time_min))
        c3.metric("Total Run Dist", f"{run_dist:.2f} km")
        c4.metric("Total Ride Dist", f"{ride_dist:.2f} km")
        
        st.divider()

        st.markdown("#### 📉 Recent Activity (Last 14 Days)")
        today = pd.to_datetime('today').normalize()
        fourteen_days_ago = today - pd.Timedelta(days=14)
        recent_df = df[df['Date'] >= fourteen_days_ago].copy()
        
        domain_start = fourteen_days_ago.strftime('%Y-%m-%d')
        domain_end = today.strftime('%Y-%m-%d')
        
        if not recent_df.empty:
            recent_df['Duration_HHMMSS'] = recent_df['Duration_min'].apply(format_duration)
            chart_recent = alt.Chart(recent_df).mark_bar(size=30, cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
                x=alt.X('Date:T', scale=alt.Scale(domain=[domain_start, domain_end]), axis=alt.Axis(format='%m-%d', tickCount='day'), title='Date (MM-DD)'),
                y=alt.Y('Duration_min:Q', title='Duration (Minutes)'),
                color=alt.Color('Type:N', scale=alt.Scale(domain=['Run', 'Ride'], range=['#2D89EF', '#2ca02c']), legend=alt.Legend(title="Sport Type", orient="top")),
                tooltip=[
                    alt.Tooltip('Date:T', title='Date', format='%Y-%m-%d'),
                    alt.Tooltip('Type:N', title='Sport'),
                    alt.Tooltip('Name:N', title='Name'),
                    alt.Tooltip('Distance_km:Q', title='Distance (km)', format='.2f'),
                    alt.Tooltip('Duration_HHMMSS:N', title='Duration')
                ]
            ).properties(height=350)
            st.altair_chart(chart_recent, use_container_width=True)
        else:
            st.info("No activities in the last 14 days. Time to get moving! 🏃‍♂️🚴‍♂️")
            
        st.divider()
        st.markdown("#### 🍩 Workout Distribution")
        
        type_counts = df['Type'].value_counts().reset_index()
        type_counts.columns = ['Type', 'Count']
        
        col_donut, col_text = st.columns([2, 1])
        with col_donut:
            donut_chart = alt.Chart(type_counts).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Type", type="nominal", scale=alt.Scale(domain=['Run', 'Ride'], range=['#2D89EF', '#2ca02c']), legend=None),
                tooltip=['Type', 'Count']
            ).properties(height=300)
            st.altair_chart(donut_chart, use_container_width=True)
            
        with col_text:
            st.write("<br><br>", unsafe_allow_html=True) 
            st.markdown("Balance your training!")
            st.write("See how your workouts are split between running and cycling. A balanced routine is key to avoiding injuries and building overall fitness.")
            for index, row in type_counts.iterrows():
                st.write(f"- **{row['Type']}s:** {row['Count']} sessions")
    else:
        st.info("Your dashboard is empty! Go to the 'Running' or 'Cycling' tabs to add your first workout. 🚀")

# ==========================================
# 🌤️ EKRAN POGODY
# ==========================================
elif st.session_state.current_view == 'Weather':
    st.markdown("<style>div.stButton > button { background: #333 !important; color: white !important; border-radius: 8px !important; aspect-ratio: auto !important; padding: 10px !important;}</style>", unsafe_allow_html=True)
    
    if st.button("⬅️ Back to Start", key="back_weather"):
        go_to_view('Home')
        st.rerun()
        
    st.header("Training Weather")
    
    saved_city = user_settings.get('city')
    
    # Zarządzanie stanem, czy użytkownik chce wpisać nowe miasto
    if 'changing_city' not in st.session_state:
        st.session_state.changing_city = False if saved_city else True
        
    if st.session_state.changing_city:
        st.markdown("### Select your city")
        st.write("Enter the city where you train to get current weather conditions.")
        new_city = st.text_input("City name", placeholder="e.g. Wrocław, Warsaw, London")
        
        if st.button("Save City"):
            if new_city.strip():
                user_settings['city'] = new_city.strip()
                save_settings(user_settings)
                st.session_state.changing_city = False
                st.rerun()
            else:
                st.error("Please enter a valid city name.")
    else:
        # Widok samej pogody
        col_w1, col_w2 = st.columns([3, 1])
        with col_w1:
            st.markdown(f"Current weather for **{saved_city}**")
        with col_w2:
            if st.button("🔄 Change City"):
                st.session_state.changing_city = True
                st.rerun()
                
        with st.spinner(f"Fetching weather data for {saved_city}..."):
            weather_data, error = get_weather(saved_city)
            
        if error:
            st.error(error)
        else:
            st.success("Data fetched successfully!")
            
            # Kafelki z danymi
            wc1, wc2, wc3 = st.columns(3)
            wc1.metric("Temperature", f"{weather_data['temp']} °C")
            wc2.metric("Feels Like", f"{weather_data['feels_like']} °C")
            wc3.metric("Wind Speed", f"{weather_data['wind']} km/h")
            
            st.divider()
            wc4, wc5, wc6 = st.columns(3)
            # 👇 Zmiana na szansę na deszcz 👇
            wc4.metric("Chance of Rain", f"{weather_data['precip_prob']} %")
            wc5.metric("Humidity", f"{weather_data['humidity']} %")
            
            # Mała rada treningowa na podstawie pogody
            st.markdown("Coach's Advice")
            # 👇 Zaktualizowana logika poradnika 👇
            if weather_data['precip_prob'] > 50:
                st.info("🌧️ High chance of rain! Take a waterproof jacket or consider an indoor session.")
            elif weather_data['precip_prob'] > 15:
                st.info("🌦️ Slight chance of rain. Keep an eye on the sky!")
            elif weather_data['temp'] > 25:
                st.warning("🔥 It's hot outside! Remember to hydrate and avoid the mid-day sun.")
            elif weather_data['temp'] < 5:
                st.info("❄️ It's chilly! Dress in layers and warm up properly before starting.")
            else:
                st.success("✅ Perfect conditions for a solid workout. Let's go!")

# ==========================================
# 🏃‍♂️ EKRAN BIEGOWY (ZE STATYSTYKAMI)
# ==========================================
elif st.session_state.current_view == 'Run':
    st.markdown("<style>div.stButton > button { background: #333 !important; color: white !important; border-radius: 8px !important; aspect-ratio: auto !important; padding: 10px !important;}</style>", unsafe_allow_html=True)
    
    if st.button("⬅️ Back to Start", key="back_run"):
        go_to_view('Home')
        st.rerun()
        
    st.header("Running Center")
    with st.expander("Add New Run"):
        with st.form("add_run_form", clear_on_submit=True):
            st.markdown("Enter your training details")
            col1, col2 = st.columns(2)
            with col1:
                new_date = st.date_input("Date", value="today")
                new_name = st.text_input("Training name", placeholder="np. Wieczorne rozbieganie")
            with col2:
                new_distance = st.number_input("Distance (km)", min_value=0.0, step=1.0, format="%.2f")
                new_duration = st.number_input("Duration time (min)", min_value=0.0, step=1.0, format="%.1f")
            
            submitted = st.form_submit_button("Save your wourkout")
            if submitted:
                if new_distance > 0 and new_duration > 0:
                    import time
                    new_id = int(time.time() * 1000)
                    new_data = pd.DataFrame({
                        'ID': [new_id], 'Date': [new_date], 'Name': [new_name],
                        'Type': ['Run'], 'Distance_km': [new_distance], 'Duration_min': [new_duration]
                    })
                    new_data.to_csv('my_workouts.csv', mode='a', header=False, index=False)
                    st.success("Training added succesfully")
                    st.rerun() 
                else:
                    st.error("Distance and time must be bigger than 0!")
    
    if not df.empty:
        runs = df[df['Type'] == 'Run'].copy()
        if not runs.empty:
            total_dist = runs['Distance_km'].sum()
            total_time = runs['Duration_min'].sum()
            avg_pace_decimal = (total_time / total_dist) if total_dist > 0 else 0
            avg_pace_str = format_pace(avg_pace_decimal)
            
            st.markdown("Overall Stats")
            mcol1, mcol2, mcol3 = st.columns(3)
            mcol1.metric(label="Total Distance", value=f"{total_dist:.2f} km")
            mcol2.metric(label="Total Runs", value=f"{len(runs)}")
            mcol3.metric(label="Average Pace", value=f"{avg_pace_str} /km")
            
            st.divider() 
            st.markdown("Distance Over Time (Last 7 Days)")
            
            today = pd.Timestamp.today().normalize()
            seven_days_ago = today - pd.Timedelta(days=6)
            last_7_days = pd.DataFrame({'Date': pd.date_range(start=seven_days_ago, end=today)})
            recent_runs = runs[(runs['Date'] >= seven_days_ago) & (runs['Date'] <= today)]
            daily_dist = recent_runs.groupby('Date')['Distance_km'].sum().reset_index()
            
            chart_data = pd.merge(last_7_days, daily_dist, on='Date', how='left').fillna({'Distance_km': 0})
            chart_data['Date_str'] = chart_data['Date'].dt.strftime('%m-%d')
            
            chart = alt.Chart(chart_data).mark_bar(color="#2D89EF").encode(
                x=alt.X('Date_str:O', title='Date (MM-DD)', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('Distance_km:Q', title='Distance (km)'),
                tooltip=[alt.Tooltip('Date_str:O', title='Date'), alt.Tooltip('Distance_km:Q', title='Distance (km)')]
            )
            st.altair_chart(chart, use_container_width=True)
            
            st.divider()
            st.markdown("Workout History")
            display_df = runs[['Date', 'Name', 'Distance_km', 'Duration_min', 'Pace_min_km']].copy()
            display_df = display_df.sort_values(by='Date', ascending=False)
            display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
            display_df['Pace /km'] = display_df['Pace_min_km'].apply(format_pace)
            display_df = display_df.drop(columns=['Pace_min_km'])
            display_df = display_df.rename(columns={'Distance_km': 'Distance (km)', 'Duration_min': 'Time (min)'})
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("Nie znaleziono żadnych treningów biegowych. Czas wyjść pobiegać! 🏃‍♂️")
    else:
        st.warning("Brak danych! Upewnij się, że plik my_workouts.csv nie jest pusty.")

# ==========================================
# 🚴‍♂️ EKRAN ROWEROWY
# ==========================================
elif st.session_state.current_view == 'Ride':
    st.markdown("<style>div.stButton > button { background: #333 !important; color: white !important; border-radius: 8px !important; aspect-ratio: auto !important; padding: 10px !important;}</style>", unsafe_allow_html=True)
    
    if st.button("⬅️ Back to Start", key="back_ride"):
        go_to_view('Home')
        st.rerun()
        
    st.header("Cycling")
    with st.expander("Add New Ride"):
        with st.form("add_ride_form", clear_on_submit=True):
            st.markdown("Enter your cycling training details")
            col1, col2 = st.columns(2)
            with col1:
                new_date = st.date_input("Date", value="today", key="ride_date")
                new_distance = st.number_input("Distance (km)", min_value=0.0, step=1.0, format="%.2f", key="ride_dist")
            with col2:
                new_name = st.text_input("Training name", placeholder="e.g., Sunday loop", key="ride_name")
                st.markdown("<p style='font-size: 14px; margin-bottom: 0px;'>Duration (HH:MM:SS)</p>", unsafe_allow_html=True)
                c_h, c_m, c_s = st.columns(3)
                with c_h:
                    h = st.number_input("Hr", min_value=0, step=1, key="r_h")
                with c_m:
                    m = st.number_input("Min", min_value=0, max_value=59, step=1, key="r_m")
                with c_s:
                    s = st.number_input("Sec", min_value=0, max_value=59, step=1, key="r_s")
            
            submitted = st.form_submit_button("Save the ride")
            if submitted:
                total_duration_min = (h * 60) + m + (s / 60)
                if new_distance > 0 and total_duration_min > 0:
                    import time
                    new_id = int(time.time() * 1000)
                    new_data = pd.DataFrame({
                        'ID': [new_id], 'Date': [new_date], 'Name': [new_name],
                        'Type': ['Ride'], 'Distance_km': [new_distance], 'Duration_min': [total_duration_min]
                    })
                    new_data.to_csv('my_workouts.csv', mode='a', header=False, index=False)
                    st.success("Cycling training added successfully!")
                    st.rerun()
                else:
                    st.error("Distance and time must be bigger than 0!")

    if not df.empty:
        rides = df[df['Type'] == 'Ride'].copy()
        if not rides.empty:
            st.markdown("Summary")
            rides['Date'] = pd.to_datetime(rides['Date'])
            rides = rides.sort_values(by='Date')
            rides['Speed_km_h'] = rides['Distance_km'] / (rides['Duration_min'] / 60)
            
            def format_duration(total_min):
                h = int(total_min // 60)
                m = int(total_min % 60)
                s = int((total_min * 60) % 60)
                return f"{h:02d}:{m:02d}:{s:02d}"
            
            rides['Duration_HHMMSS'] = rides['Duration_min'].apply(format_duration)
            total_rides = len(rides) 
            total_dist = rides['Distance_km'].sum()
            avg_speed = rides['Speed_km_h'].mean()
            total_time_min = rides['Duration_min'].sum()
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Rides", f"{total_rides}")
            c2.metric("Total Distance", f"{total_dist:.2f} km")
            c3.metric("Time in Saddle", format_duration(total_time_min))
            c4.metric("Avg Speed", f"{avg_speed:.1f} km/h")
            
            st.divider()
            st.markdown("### 📊 Last 7 Days")
            today = pd.to_datetime('today').normalize()
            seven_days_ago = today - pd.Timedelta(days=7)
            recent_rides = rides[rides['Date'] >= seven_days_ago]
            
            domain_start = seven_days_ago.strftime('%Y-%m-%d')
            domain_end = today.strftime('%Y-%m-%d')
            
            if not recent_rides.empty:
                chart_dist = alt.Chart(recent_rides).mark_bar(color='#2ca02c', size=40, cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
                    x=alt.X('Date:T', scale=alt.Scale(domain=[domain_start, domain_end]), axis=alt.Axis(format='%m-%d', tickCount='day'), title='Date (MM-DD)'),
                    y=alt.Y('Distance_km:Q', title='Distance (km)', scale=alt.Scale(domainMin=0)),
                    tooltip=[
                        alt.Tooltip('Date:T', title='Date', format='%Y-%m-%d'),
                        alt.Tooltip('Name:N', title='Name'),
                        alt.Tooltip('Distance_km:Q', title='Distance (km)', format='.2f'),
                        alt.Tooltip('Duration_HHMMSS:N', title='Duration'),
                        alt.Tooltip('Speed_km_h:Q', title='Speed (km/h)', format='.1f')
                    ]
                ).properties(height=300, title='Distance Over Time (Last 7 Days)')
                st.altair_chart(chart_dist, use_container_width=True)
            else:
                st.info("No rides in the last 7 days. Time to get back on the bike! 🚲")
                
            st.markdown(" All Rides History")
            display_rides = rides[['Date', 'Name', 'Distance_km', 'Duration_HHMMSS', 'Speed_km_h']].copy()
            display_rides['Date'] = display_rides['Date'].dt.strftime('%Y-%m-%d')
            display_rides['Distance_km'] = display_rides['Distance_km'].apply(lambda x: f"{x:.2f} km")
            display_rides['Speed_km_h'] = display_rides['Speed_km_h'].apply(lambda x: f"{x:.1f} km/h")
            
            display_rides = display_rides.rename(columns={'Date': 'Date', 'Name': 'Training Name', 'Distance_km': 'Distance', 'Duration_HHMMSS': 'Duration', 'Speed_km_h': 'Avg Speed'})
            display_rides = display_rides.sort_index(ascending=False)
            st.dataframe(display_rides, hide_index=True, use_container_width=True)
        else:
            st.info("No cycling workouts found.")

# ==========================================
# 🏆 EKRAN REKORDÓW
# ==========================================
elif st.session_state.current_view == 'Records':
    st.markdown("<style>div.stButton > button { background: #333 !important; color: white !important; border-radius: 8px !important; aspect-ratio: auto !important; padding: 10px !important;}</style>", unsafe_allow_html=True)
    
    if st.button("⬅️ Back to Start", key="back_records"):
        go_to_view('Home')
        st.rerun()
        
    st.header("Personal Bests")
    if not df.empty:
        runs = df[df['Type'] == 'Run'].copy()
        if not runs.empty:
            st.markdown("Running Records")
            longest_run = runs.loc[runs['Distance_km'].idxmax()]
            longest_time = runs.loc[runs['Duration_min'].idxmax()]
            
            valid_pace_runs = runs[runs['Distance_km'] > 0]
            if not valid_pace_runs.empty:
                best_pace_run = valid_pace_runs.loc[valid_pace_runs['Pace_min_km'].idxmin()]
            else:
                best_pace_run = None

            col1, col2, col3 = st.columns(3)
            with col1:
                st.success("Longest Distance")
                date_str = longest_run['Date'].strftime('%Y-%m-%d')
                st.metric(label=f"{longest_run['Name']} ({date_str})", value=f"{longest_run['Distance_km']:.2f} km")
            with col2:
                st.info("Longest Time")
                date_str = longest_time['Date'].strftime('%Y-%m-%d')
                st.metric(label=f"{longest_time['Name']} ({date_str})", value=f"{longest_time['Duration_min']:.2f} min")
            with col3:
                st.warning("⚡ Best Pace")
                if best_pace_run is not None:
                    date_str = best_pace_run['Date'].strftime('%Y-%m-%d')
                    st.metric(label=f"{best_pace_run['Name']} ({date_str})", value=f"{format_pace(best_pace_run['Pace_min_km'])} /km")
                else:
                    st.metric(label="N/A", value="-:-- /km")
            st.divider()
            st.markdown("<p style='text-align: center; color: gray;'>Keep pushing your limits! 🔥</p>", unsafe_allow_html=True)
        else:
            st.info("Brak treningów biegowych, żeby wyliczyć rekordy. Czas zrobić pierwszy trening! 🏃‍♂️")
    else:
        st.warning("Brak danych! Upewnij się, że plik my_workouts.csv nie jest pusty.")