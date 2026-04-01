import streamlit as st
import pandas as pd
import altair as alt

# 1. Konfiguracja Strony
st.set_page_config(page_title="Sport Analyzer", page_icon="🏆", layout="centered")

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

# 3. Wczytanie danych
try:
    df = pd.read_csv('my_workouts.csv')
    
    # Konwertujemy kolumnę 'Date' na prawdziwy format daty
    df['Date'] = pd.to_datetime(df['Date'])
    
    df['Pace_min_km'] = df.apply(lambda row: row['Duration_min'] / row['Distance_km'] if row['Distance_km'] > 0 else 0, axis=1)
    total_runs = len(df[df['Type'] == 'Run'])
except FileNotFoundError:
    df = pd.DataFrame() 
    total_runs = 0

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
            <h1 style='margin: 0; font-size: 32px;'>👋 Welcome back, Kacper!</h1>
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
        if st.button("🚴‍♂️ CYCLING", key="btn_ride", use_container_width=True):
            go_to_view('Ride')
            st.rerun()
            
    with col3:
        st.markdown('<span class="css-hook-weather"></span>', unsafe_allow_html=True)
        if st.button("🌤️ WEATHER\nWrocław", key="btn_weather", use_container_width=True):
            st.toast("Weather coming soon! 🌤️")

    st.write("") 

    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown('<span class="css-hook-rec"></span>', unsafe_allow_html=True)
        if st.button("🏆 RECORDS\n\nPersonal bests", key="btn_rec", use_container_width=True):
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

# ==========================================
# 🏃‍♂️ EKRAN BIEGOWY (ZE STATYSTYKAMI)
# ==========================================
elif st.session_state.current_view == 'Run':
    st.markdown("<style>div.stButton > button { background: #333 !important; color: white !important; border-radius: 8px !important; aspect-ratio: auto !important; padding: 10px !important;}</style>", unsafe_allow_html=True)
    
    if st.button("⬅️ Back to Start", key="back_run"):
        go_to_view('Home')
        st.rerun()
        
    st.header("Running Center")
    # ==========================================
    # ➕ FORMULARZ DODAWANIA BIEGU
    # ==========================================
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
            
            # Przycisk zapisu wewnątrz formularza
            submitted = st.form_submit_button("Save your wourkout")
            
            if submitted:
                if new_distance > 0 and new_duration > 0:
                    # Generujemy unikalne ID na podstawie aktualnego czasu (podobnie jak robi to Strava)
                    import time
                    new_id = int(time.time() * 1000)
                    
                    # Tworzenie nowego wiersza DOKŁADNIE pod strukturę Twojego pliku
                    new_data = pd.DataFrame({
                        'ID': [new_id],
                        'Date': [new_date],
                        'Name': [new_name],
                        'Type': ['Run'], 
                        'Distance_km': [new_distance],
                        'Duration_min': [new_duration]
                    })
                    
                    # Dopisanie do pliku CSV (bez nagłówków, na sam dół)
                    new_data.to_csv('my_workouts.csv', mode='a', header=False, index=False)
                    
                    st.success("✅ Training added succesfully")
                    st.rerun() # Odświeża aplikację
                else:
                    st.error("Distance and time must be bigger than 0!")
    
    if not df.empty:
        runs = df[df['Type'] == 'Run'].copy()
        
        if not runs.empty:
            # --- 1. OBLICZANIE STATYSTYK ---
            total_dist = runs['Distance_km'].sum()
            total_time = runs['Duration_min'].sum()
            
            avg_pace_decimal = (total_time / total_dist) if total_dist > 0 else 0
            avg_pace_str = format_pace(avg_pace_decimal)
            
            # --- 2. WYŚWIETLANIE METRYK ---
            st.markdown("Overall Stats")
            mcol1, mcol2, mcol3 = st.columns(3)
            mcol1.metric(label="Total Distance", value=f"{total_dist:.2f} km")
            mcol2.metric(label="Total Runs", value=f"{len(runs)}")
            mcol3.metric(label="Average Pace", value=f"{avg_pace_str} /km")
            
            st.divider() 
            
            # --- 3. WYKRES SŁUPKOWY (OSTATNIE 7 DNI - SZTYWNY) ---
            st.markdown("Distance Over Time (Last 7 Days)")
            
            # Obliczamy dzisiejszą datę i datę sprzed 6 dni (żeby mieć pełne 7 dni)
            today = pd.Timestamp.today().normalize()
            seven_days_ago = today - pd.Timedelta(days=6)
            
            # Tworzymy szkielet z rygorystycznymi 7 dniami
            last_7_days = pd.DataFrame({'Date': pd.date_range(start=seven_days_ago, end=today)})
            
            # Filtrujemy tylko biegi z tych 7 dni
            recent_runs = runs[(runs['Date'] >= seven_days_ago) & (runs['Date'] <= today)]
            daily_dist = recent_runs.groupby('Date')['Distance_km'].sum().reset_index()
            
            # Łączymy szkielet z danymi, uzupełniając brakujące dni zerami
            chart_data = pd.merge(last_7_days, daily_dist, on='Date', how='left').fillna({'Distance_km': 0})
            
            # Formatujemy datę do ładnego stringa np. "03-31", żeby wykres był "sztywny"
            chart_data['Date_str'] = chart_data['Date'].dt.strftime('%m-%d')
            
            # Budujemy wykres
            chart = alt.Chart(chart_data).mark_bar(color="#2D89EF").encode(
                x=alt.X('Date_str:O', title='Date (MM-DD)', axis=alt.Axis(labelAngle=0)), # O = Ordinal (dyskretne kategorie na osi)
                y=alt.Y('Distance_km:Q', title='Distance (km)'),
                tooltip=[alt.Tooltip('Date_str:O', title='Date'), alt.Tooltip('Distance_km:Q', title='Distance (km)')]
            )
            
            # Renderowanie wykresu (domyślnie zablokowane zbliżanie, jeśli nie ma .interactive())
            st.altair_chart(chart, use_container_width=True)
            
            st.divider()
            
            # --- 4. HISTORIA TRENINGÓW ---
            st.markdown("Workout History")
            display_df = runs[['Date', 'Name', 'Distance_km', 'Duration_min', 'Pace_min_km']].copy()
            
            # Sortujemy tabelę malejąco według daty (najnowsze na górze)
            display_df = display_df.sort_values(by='Date', ascending=False)
            
            display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
            display_df['Pace /km'] = display_df['Pace_min_km'].apply(format_pace)
            display_df = display_df.drop(columns=['Pace_min_km'])
            display_df = display_df.rename(columns={
                'Distance_km': 'Distance (km)', 
                'Duration_min': 'Time (min)'
            })
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
        else:
            st.info("Nie znaleziono żadnych treningów biegowych. Czas wyjść pobiegać! 🏃‍♂️")
    else:
        st.warning("Brak danych! Upewnij się, że plik my_workouts.csv nie jest pusty.")

# ==========================================
# EKRAN ROWEROWY
# ==========================================
elif st.session_state.current_view == 'Ride':
    st.markdown("<style>div.stButton > button { background: #333 !important; color: white !important; border-radius: 8px !important; aspect-ratio: auto !important; padding: 10px !important;}</style>", unsafe_allow_html=True)
    
    if st.button("⬅️ Back to Start", key="back_ride"):
        go_to_view('Home')
        st.rerun()
        
    st.header("Cycling")
    # --- ➕ FORMULARZ DODAWANIA JAZDY ---
    with st.expander("Add New Ride"):
        with st.form("add_ride_form", clear_on_submit=True):
            st.markdown("Enter your cycling training details")
            
            col1, col2 = st.columns(2)
            with col1:
                new_date = st.date_input("Date", value="today", key="ride_date")
                new_distance = st.number_input("Distance (km)", min_value=0.0, step=1.0, format="%.2f", key="ride_dist")
            
            with col2:
                new_name = st.text_input("Training name", placeholder="e.g., Sunday loop", key="ride_name")
                
                # Etykieta dla czasu
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
                # Obliczamy łączny czas w minutach z podanych godzin, minut i sekund
                total_duration_min = (h * 60) + m + (s / 60)
                
                if new_distance > 0 and total_duration_min > 0:
                    import time
                    new_id = int(time.time() * 1000)
                    
                    new_data = pd.DataFrame({
                        'ID': [new_id],
                        'Date': [new_date],
                        'Name': [new_name],
                        'Type': ['Ride'], 
                        'Distance_km': [new_distance],
                        'Duration_min': [total_duration_min]
                    })
                    
                    new_data.to_csv('my_workouts.csv', mode='a', header=False, index=False)
                    st.success("Cycling training added successfully!")
                    st.rerun()
                else:
                    st.error("Distance and time must be bigger than 0!")

    # --- 📊 CYCLING DATA VIEW ---
    if not df.empty:
        # Filtrujemy tylko rowery
        rides = df[df['Type'] == 'Ride'].copy()
        
        if not rides.empty:
            st.markdown("Summary")
            
            # Upewniamy się, że data to faktycznie "data" dla kodu i sortujemy
            rides['Date'] = pd.to_datetime(rides['Date'])
            rides = rides.sort_values(by='Date')
            
            # Obliczamy Prędkość w km/h
            rides['Speed_km_h'] = rides['Distance_km'] / (rides['Duration_min'] / 60)
            
            # Funkcja zamieniająca minuty na tekst HH:MM:SS
            def format_duration(total_min):
                h = int(total_min // 60)
                m = int(total_min % 60)
                s = int((total_min * 60) % 60)
                return f"{h:02d}:{m:02d}:{s:02d}"
            
            # Tworzymy nową kolumnę z ładnym formatem czasu
            rides['Duration_HHMMSS'] = rides['Duration_min'].apply(format_duration)
            
            # Statystyki do kafelków
            total_rides = len(rides)  # <--- TUTAJ LICZYMY ILOŚĆ TRENINGÓW
            total_dist = rides['Distance_km'].sum()
            avg_speed = rides['Speed_km_h'].mean()
            total_time_min = rides['Duration_min'].sum()
            
            # Dzielimy na 4 kolumny zamiast 3
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Rides", f"{total_rides}")
            c2.metric("Total Distance", f"{total_dist:.2f} km")
            c3.metric("Time in Saddle", format_duration(total_time_min))
            c4.metric("Avg Speed", f"{avg_speed:.1f} km/h")
            
            st.divider()
            
            # --- WIDOK 7 DNI (WYKRES) ---
            st.markdown("### 📊 Last 7 Days")
            
            today = pd.to_datetime('today').normalize()
            seven_days_ago = today - pd.Timedelta(days=7)
            recent_rides = rides[rides['Date'] >= seven_days_ago]
            
            # Formaty tekstowe dat do usztywnienia osi X
            domain_start = seven_days_ago.strftime('%Y-%m-%d')
            domain_end = today.strftime('%Y-%m-%d')
            
            if not recent_rides.empty:
                chart_dist = alt.Chart(recent_rides).mark_bar(
                    color='#2ca02c', 
                    size=40,  
                    cornerRadiusTopLeft=3, 
                    cornerRadiusTopRight=3
                ).encode(
                    x=alt.X('Date:T',
                          scale=alt.Scale(domain=[domain_start, domain_end]), # <-- TO USZTYWNIA OŚ NA 7 DNI
                          axis=alt.Axis(
                              format='%m-%d',
                              tickCount='day'
                          ),
                          title='Date (MM-DD)'
                    ),
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
                
            # --- TABELA ZE WSZYSTKIMI TRENINGAMI ---
            st.markdown(" All Rides History")
            
            # Przygotowujemy ładną tabelkę do wyświetlenia
            display_rides = rides[['Date', 'Name', 'Distance_km', 'Duration_HHMMSS', 'Speed_km_h']].copy()
            
            # Formatujemy dane pod człowieka, żeby w tabeli wyglądały jak z profesjonalnej apki
            display_rides['Date'] = display_rides['Date'].dt.strftime('%Y-%m-%d')
            display_rides['Distance_km'] = display_rides['Distance_km'].apply(lambda x: f"{x:.2f} km")
            display_rides['Speed_km_h'] = display_rides['Speed_km_h'].apply(lambda x: f"{x:.1f} km/h")
            
            # Zmieniamy nazwy kolumn
            display_rides = display_rides.rename(columns={
                'Date': 'Date', 
                'Name': 'Training Name', 
                'Distance_km': 'Distance', 
                'Duration_HHMMSS': 'Duration',
                'Speed_km_h': 'Avg Speed'
            })
            
            # Odwracamy kolejność, żeby najnowsze treningi były na samej górze (malejąco)
            display_rides = display_rides.sort_index(ascending=False)
            
            # Wyświetlamy jako ładną ramkę danych (st.dataframe)
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
            
            # --- WYLICZANIE REKORDÓW ---
            # 1. Najdłuższy dystans (szukamy indeksu z maksymalną wartością i pobieramy cały wiersz)
            longest_run = runs.loc[runs['Distance_km'].idxmax()]
            
            # 2. Najdłuższy czas trwania
            longest_time = runs.loc[runs['Duration_min'].idxmax()]
            
            # 3. Najlepsze tempo (szukamy najmniejszej wartości min/km, ale tylko dla biegów > 0 km)
            valid_pace_runs = runs[runs['Distance_km'] > 0]
            if not valid_pace_runs.empty:
                best_pace_run = valid_pace_runs.loc[valid_pace_runs['Pace_min_km'].idxmin()]
            else:
                best_pace_run = None

            # --- WYŚWIETLANIE (Trzy ładne kolumny) ---
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