import streamlit as st
import holidays
import pandas as pd
from datetime import date, timedelta

# --- Page Configuration ---
st.set_page_config(
    page_title="Holiday Optimizer",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Translations Dictionary ---
TRANSLATIONS = {
    "TR": {
        "title": "Tatil Planlayıcı",
        "subtitle": "Minimum yıllık izinle maksimum tatil yapın.",
        "settings": "Ayarlar",
        "select_country": "Ülke Seçimi",
        "select_state": "Eyalet Seçimi (Almanya)",
        "year": "Yıl",
        "max_leave": "Maksimum Köprü İzni",
        "max_leave_help": "İki tatili birleştirmek için en fazla kaç gün yıllık izin harcamak istersiniz?",
        "calc_btn": "Hesapla ve Listele",
        "analyzing": "Takvim taranıyor...",
        "best_opp": "En İyi Fırsat",
        "all_opps": "Tüm Fırsatlar",
        "leave_needed": "Harcanacak İzin",
        "total_vac": "Toplam Tatil",
        "efficiency": "Verimlilik Puanı",
        "date_range": "Tarih Aralığı",
        "reason": "Sebep",
        "days": "Gün",
        "option": "Seçenek",
        "error_not_found": "Bu kriterlere uygun fırsat bulunamadı. İzin limitini artırmayı deneyin.",
        "info_start": "Soldaki menüden ayarları seçip butona basın."
    },
    "DE": {
        "title": "Urlaubsplaner",
        "subtitle": "Maximale Urlaubstage mit minimalem Urlaubseinsatz.",
        "settings": "Einstellungen",
        "select_country": "Land auswählen",
        "select_state": "Bundesland auswählen",
        "year": "Jahr",
        "max_leave": "Max. Brückentage",
        "max_leave_help": "Wie viele Urlaubstage möchten Sie maximal investieren, um Feiertage zu verbinden?",
        "calc_btn": "Berechnen",
        "analyzing": "Kalender wird analysiert...",
        "best_opp": "Beste Option",
        "all_opps": "Alle Möglichkeiten",
        "leave_needed": "Benötigte Urlaubstage",
        "total_vac": "Gesamter Urlaub",
        "efficiency": "Effizienz",
        "date_range": "Zeitraum",
        "reason": "Grund",
        "days": "Tage",
        "option": "Option",
        "error_not_found": "Keine Brückentage gefunden. Versuchen Sie, das Limit zu erhöhen.",
        "info_start": "Wählen Sie Ihre Einstellungen und klicken Sie auf Berechnen."
    },
    "PL": {
        "title": "Optymalizator Urlopu",
        "subtitle": "Maksymalny wypoczynek przy minimalnym zużyciu urlopu.",
        "settings": "Ustawienia",
        "select_country": "Wybierz kraj",
        "select_state": "Wybierz region (Niemcy)",
        "year": "Rok",
        "max_leave": "Maks. dni urlopowe",
        "max_leave_help": "Ile dni urlopu chcesz wykorzystać, aby połączyć święta?",
        "calc_btn": "Oblicz",
        "analyzing": "Analizowanie kalendarza...",
        "best_opp": "Najlepsza Oferta",
        "all_opps": "Wszystkie Opcje",
        "leave_needed": "Wymagany Urlop",
        "total_vac": "Całkowity Wypoczynek",
        "efficiency": "Efektywność",
        "date_range": "Data",
        "reason": "Powód",
        "days": "Dni",
        "option": "Opcja",
        "error_not_found": "Nie znaleziono okazji. Spróbuj zwiększyć limit dni.",
        "info_start": "Wybierz ustawienia z paska bocznego i kliknij przycisk."
    }
}

# --- Constants ---
DE_STATES = {
    "Baden-Württemberg": "BW", "Bavaria (Bayern)": "BY", "Berlin": "BE", 
    "Brandenburg": "BB", "Bremen": "HB", "Hamburg": "HH", 
    "Hesse (Hessen)": "HE", "Mecklenburg-Vorpommern": "MV", 
    "Lower Saxony (Niedersachsen)": "NI", "North Rhine-Westphalia (NRW)": "NW", 
    "Rhineland-Palatinate": "RP", "Saarland": "SL", "Saxony (Sachsen)": "SN", 
    "Saxony-Anhalt": "ST", "Schleswig-Holstein": "SH", "Thuringia (Thüringen)": "TH"
}

# --- CSS Styling ---
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Logic ---
with st.sidebar:
    # Default to TR initially, but text updates after selection
    country_choice = st.selectbox(
        "Select Country / Ülke / Land / Kraj", 
        ["TR", "DE", "PL"], 
        format_func=lambda x: {"TR": "Türkiye 🇹🇷", "DE": "Deutschland 🇩🇪", "PL": "Polska 🇵🇱"}[x]
    )
    
    # Get the dictionary for the selected language
    T = TRANSLATIONS[country_choice]
    
    st.header(T["settings"])
    
    state_code = None
    if country_choice == "DE":
        selected_state_name = st.selectbox(T["select_state"], list(DE_STATES.keys()))
        state_code = DE_STATES[selected_state_name]

    year = st.number_input(T["year"], min_value=2024, max_value=2030, value=2026)
    
    max_bridge = st.slider(
        T["max_leave"], 
        1, 5, 2, 
        help=T["max_leave_help"]
    )
    
    st.markdown("---")

# --- Main UI ---
st.title(T["title"])
st.markdown(T["subtitle"])

# --- Helper Functions ---

def get_holidays(country, year, subdiv=None):
    if country == "TR":
        return holidays.TR(years=year)
    elif country == "PL":
        return holidays.PL(years=year)
    elif country == "DE":
        return holidays.DE(years=year, subdiv=subdiv) if subdiv else holidays.DE(years=year)
    return {}

def calculate_opportunities(country, year, bridge_limit, subdiv=None):
    holidays_dict = get_holidays(country, year, subdiv)
    
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    all_days = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    
    # 1: Holiday/Weekend, 0: Work Day
    day_status = [1 if (d in holidays_dict or d.weekday() >= 5) else 0 for d in all_days]
    
    opps = []
    i = 0
    while i < len(all_days):
        if day_status[i] == 0: 
            temp_i = i
            work_days_count = 0
            while temp_i < len(all_days) and day_status[temp_i] == 0:
                work_days_count += 1
                temp_i += 1
            
            if work_days_count <= bridge_limit:
                prev_holiday = (i > 0 and day_status[i-1] == 1)
                next_holiday = (temp_i < len(all_days) and day_status[temp_i] == 1)
                
                if prev_holiday and next_holiday:
                    start_idx = i - 1
                    while start_idx >= 0 and day_status[start_idx] == 1:
                        start_idx -= 1
                    start_real = all_days[start_idx + 1]
                    
                    end_idx = temp_i
                    while end_idx < len(all_days) and day_status[end_idx] == 1:
                        end_idx += 1
                    end_real = all_days[end_idx - 1]
                    
                    total_off = (end_real - start_real).days + 1
                    
                    names = {holidays_dict.get(d) for d in [all_days[k] for k in range(start_idx+1, end_idx)] if d in holidays_dict}
                    
                    opps.append({
                        "start": start_real,
                        "end": end_real,
                        "used_leave": work_days_count,
                        "total_off": total_off,
                        "efficiency": round(total_off / work_days_count, 1) if work_days_count > 0 else total_off,
                        "reason": ", ".join(names) if names else "Weekend"
                    })
            i = temp_i
        else:
            i += 1
            
    return pd.DataFrame(opps)

# --- Calculation Logic ---

if st.button(T["calc_btn"], type="primary", use_container_width=True):
    with st.spinner(T["analyzing"]):
        df = calculate_opportunities(country_choice, year, max_bridge, state_code)
    
    if not df.empty:
        df = df.sort_values(by=["efficiency", "total_off"], ascending=False).reset_index(drop=True)
        best = df.iloc[0]
        
        st.subheader(T["best_opp"])
        c1, c2, c3 = st.columns(3)
        c1.metric(T["leave_needed"], f"{best['used_leave']}")
        c2.metric(T["total_vac"], f"{best['total_off']} {T['days']}")
        c3.metric(T["efficiency"], f"{best['efficiency']}x")
        
        st.success(f"{T['date_range']}: {best['start'].strftime('%d.%m.%Y')} - {best['end'].strftime('%d.%m.%Y')} | {T['reason']}: {best['reason']}")
        
        st.subheader(T["all_opps"])
        
        for idx, row in df.iterrows():
            with st.expander(f"{T['option']} {idx+1}: {row['total_off']} {T['days']} ({row['used_leave']} {T['leave_needed']})"):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"**{T['date_range']}:** {row['start'].strftime('%d %B')} - {row['end'].strftime('%d %B %Y')}")
                    st.write(f"**{T['reason']}:** {row['reason']}")
                with col_b:
                    st.caption(T["efficiency"])
                    st.progress(min(row['efficiency'] / 5, 1.0))
    else:
        st.error(T["error_not_found"])
else:
    st.info(T["info_start"])