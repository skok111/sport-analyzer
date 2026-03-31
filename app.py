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
    
    if not df.empty:
        runs = df[df['Type'] == 'Run'].copy()
        
        if not runs.empty:
            # --- 1. OBLICZANIE STATYSTYK ---
            total_dist = runs['Distance_km'].sum()
            total_time = runs['Duration_min'].sum()
            
            avg_pace_decimal = (total_time / total_dist) if total_dist > 0 else 0
            avg_pace_str = format_pace(avg_pace_decimal)
            
            # --- 2. WYŚWIETLANIE METRYK ---
            st.markdown("### 📈 Overall Stats")
            mcol1, mcol2, mcol3 = st.columns(3)
            mcol1.metric(label="Total Distance", value=f"{total_dist:.2f} km")
            mcol2.metric(label="Total Runs", value=f"{len(runs)}")
            mcol3.metric(label="Average Pace", value=f"{avg_pace_str} /km")
            
            st.divider() 
            
            # --- 3. WYKRES SŁUPKOWY (OSTATNIE 7 DNI - SZTYWNY) ---
            st.markdown("### 📊 Distance Over Time (Last 7 Days)")
            
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
            st.markdown("### 📝 Workout History")
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
# 🚴‍♂️ EKRAN ROWEROWY
# ==========================================
elif st.session_state.current_view == 'Ride':
    st.markdown("<style>div.stButton > button { background: #333 !important; color: white !important; border-radius: 8px !important; aspect-ratio: auto !important; padding: 10px !important;}</style>", unsafe_allow_html=True)
    
    if st.button("⬅️ Back to Start", key="back_ride"):
        go_to_view('Home')
        st.rerun()
        
    st.header("🚴‍♂️ Cycling")
    st.write("WIP (Work in Progress)")

# ==========================================
# 🏆 EKRAN REKORDÓW
# ==========================================
elif st.session_state.current_view == 'Records':
    st.markdown("<style>div.stButton > button { background: #333 !important; color: white !important; border-radius: 8px !important; aspect-ratio: auto !important; padding: 10px !important;}</style>", unsafe_allow_html=True)
    
    if st.button("⬅️ Back to Start", key="back_records"):
        go_to_view('Home')
        st.rerun()
        
    st.header("🏆 Personal Bests")
    st.write("WIP (Work in Progress)")