import streamlit as st
import holidays
import pandas as pd
from datetime import date, timedelta

# ==========================================
# 1. AYARLAR, CSS VE DIL PAKETI
# ==========================================
# GÜNCELLEME: page_icon="✈️" eklendi.
st.set_page_config(page_title="Smart Leave", page_icon="✈️", layout="wide", initial_sidebar_state="auto")

# CSS: GÜNCELLEME: Streamlit menülerini gizleyen kodlar eklendi.
st.markdown("""
<style>
    /* --- STREAMLIT BRANDING GİZLEME --- */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* --- MEVCUT TASARIM --- */
    .metric-card {
        background-color: #FFFFFF !important;
        border: 1px solid #dcdcdc;
        border-radius: 6px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        height: 100%;
        margin-bottom: 10px;
    }
    .metric-label {
        font-size: 12px;
        color: #333333 !important;
        margin-bottom: 5px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #000000 !important;
        margin: 0;
    }
    .stLinkButton a {
        font-weight: bold !important;
        text-align: center !important;
        text-decoration: none !important;
    }
    /* Mobilde fontlari duzenle */
    @media only screen and (max-width: 600px) {
        .metric-value { font-size: 20px !important; }
        .metric-label { font-size: 10px !important; }
        .block-container { padding-top: 2rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# --- COKLU DIL SOZLUGU ---
# Her ulke kodu icin arayuz metinleri
TEXTS = {
    "TR": {
        "title": "Tatil Planlayıcı",
        "desc": "Resmi tatilleri hafta sonlarıyla birleştirerek minimum izinle maksimum tatil yapın.",
        "settings": "Ayarlar",
        "country": "Ülke Seçiniz",
        "state": "Eyalet (Bundesland)",
        "year": "Yıl",
        "date_range": "Tarih Aralığı",
        "max_bridge": "Maksimum İzin Kullanımı (Gün)",
        "calc_btn": "HESAPLA",
        "best_option": "En İyi Fırsat",
        "vacation_days": "Toplam Tatil",
        "leave_days": "Harcanacak İzin",
        "efficiency": "Verimlilik",
        "all_options": "Tüm Fırsatlar",
        "reason": "Sebep",
        "check_flight": "Uçak Bileti Bak",
        "check_hotel": "Otel Fiyatlarına Bak",
        "cta_text": "Bu tarihler için fiyatları gör:",
        "warn_no_result": "Kriterlere uygun sonuç bulunamadı.",
        "error_date": "Lütfen geçerli bir tarih aralığı seçiniz.",
        "info_start": "Hesaplama yapmak için menüyü kullanın."
    },
    "DE": {
        "title": "Urlaubsplaner",
        "desc": "Verbinden Sie Feiertage mit Wochenenden fur maximalen Urlaub bei minimalen Urlaubstagen.",
        "settings": "Einstellungen",
        "country": "Land auswahlen",
        "state": "Bundesland",
        "year": "Jahr",
        "date_range": "Datumsbereich",
        "max_bridge": "Max. Bruckentage",
        "calc_btn": "BERECHNEN",
        "best_option": "Beste Option",
        "vacation_days": "Urlaubstage (Gesamt)",
        "leave_days": "Benotigte Urlaubstage",
        "efficiency": "Effizienz",
        "all_options": "Alle Optionen",
        "reason": "Grund",
        "check_flight": "Fluge suchen",
        "check_hotel": "Hotels suchen",
        "cta_text": "Angebote prufen:",
        "warn_no_result": "Keine passenden Bruckentage gefunden.",
        "error_date": "Bitte wahlen Sie einen gultigen Datumsbereich.",
        "info_start": "Benutzen Sie das Menu, um zu starten."
    },
    "EN": { # Varsayilan (US, GB)
        "title": "Smart Leave",
        "desc": "Combine public holidays with weekends to maximize your vacation with minimum leave.",
        "settings": "Settings",
        "country": "Select Country",
        "state": "Select State",
        "year": "Year",
        "date_range": "Date Range",
        "max_bridge": "Max Leave Days Used",
        "calc_btn": "CALCULATE",
        "best_option": "Best Opportunity",
        "vacation_days": "Total Vacation",
        "leave_days": "Leave Days Used",
        "efficiency": "Efficiency",
        "all_options": "All Opportunities",
        "reason": "Reason",
        "check_flight": "Check Flights",
        "check_hotel": "Check Hotels",
        "cta_text": "Check prices for these dates:",
        "warn_no_result": "No matching opportunities found.",
        "error_date": "Please select a valid date range.",
        "info_start": "Use the menu to start calculation."
    },
    "PL": {
        "title": "Planer Urlopu",
        "desc": "Polacz dni wolne z weekendami, aby uzyskac maksymalny urlop przy minimalnym wykorzystaniu dni wolnych.",
        "settings": "Ustawienia",
        "country": "Wybierz Kraj",
        "state": "Wojewodztwo",
        "year": "Rok",
        "date_range": "Zakres Dat",
        "max_bridge": "Maks. dni urlopu",
        "calc_btn": "OBLICZ",
        "best_option": "Najlepsza Opcja",
        "vacation_days": "Calkowity Urlop",
        "leave_days": "Zuzyty Urlop",
        "efficiency": "Wydajnosc",
        "all_options": "Wszystkie Opcje",
        "reason": "Powod",
        "check_flight": "Sprawdz Loty",
        "check_hotel": "Sprawdz Hotele",
        "cta_text": "Sprawdz ceny:",
        "warn_no_result": "Nie znaleziono pasujacych opcji.",
        "error_date": "Prosze wybrac prawidlowy zakres dat.",
        "info_start": "Uzyj menu, aby rozpoczac."
    }
}

# Almanya Eyalet Kodlari
GERMAN_STATES = {
    "BW": "Baden-Wurttemberg", "BY": "Bayern", "BE": "Berlin",
    "BB": "Brandenburg", "HB": "Bremen", "HH": "Hamburg",
    "HE": "Hessen", "MV": "Mecklenburg-Vorpommern", "NI": "Niedersachsen",
    "NW": "Nordrhein-Westfalen", "RP": "Rheinland-Pfalz", "SL": "Saarland",
    "SN": "Sachsen", "ST": "Sachsen-Anhalt", "SH": "Schleswig-Holstein",
    "TH": "Thuringen"
}

# Ulke Listesi (Kod -> Ekranda Gorunecek Isim)
COUNTRY_OPTIONS = {
    "US": "United States", # Varsayilan (EN)
    "GB": "United Kingdom",
    "TR": "Turkey",
    "DE": "Germany",
    "PL": "Poland"
}

# ==========================================
# 2. HESAPLAMA MANTIGI
# ==========================================

def get_holidays_range(country_code, start_date, end_date, subdiv=None):
    years = list(range(start_date.year, end_date.year + 1))
    
    if country_code == "DE":
        return holidays.DE(years=years, subdiv=subdiv)
    elif country_code == "TR":
        return holidays.TR(years=years)
    elif country_code == "PL":
        return holidays.PL(years=years)
    elif country_code == "US":
        return holidays.US(years=years)
    elif country_code == "GB":
        return holidays.GB(years=years)
    return {}

def is_weekend(d):
    return d.weekday() >= 5

def optimize_holidays(country_code, start_date, end_date, max_bridge_days, subdiv=None):
    holidays_dict = get_holidays_range(country_code, start_date, end_date, subdiv)
    delta = (end_date - start_date).days
    all_days = [start_date + timedelta(days=i) for i in range(delta + 1)]
    
    day_status = [1 if (d in holidays_dict or is_weekend(d)) else 0 for d in all_days]
    opportunities = []
    
    i = 0
    while i < len(all_days):
        if day_status[i] == 0:
            work_streak = 0
            temp_i = i
            while temp_i < len(all_days) and day_status[temp_i] == 0:
                work_streak += 1
                temp_i += 1
            
            if work_streak <= max_bridge_days:
                prev_is_holiday = True if i == 0 else (day_status[i-1] == 1)
                next_is_holiday = True if temp_i == len(all_days) else (day_status[temp_i] == 1)
                
                if prev_is_holiday and next_is_holiday:
                    start_idx = i - 1
                    while start_idx >= 0 and day_status[start_idx] == 1:
                        start_idx -= 1
                    start_idx += 1 
                    
                    end_idx = temp_i
                    while end_idx < len(all_days) and day_status[end_idx] == 1:
                        end_idx += 1
                    end_idx -= 1
                    
                    total_vacation = (all_days[end_idx] - all_days[start_idx]).days + 1
                    
                    holiday_names = set()
                    for k in range(start_idx, end_idx + 1):
                        d_check = all_days[k]
                        if d_check in holidays_dict:
                            holiday_names.add(holidays_dict.get(d_check))
                    
                    opportunities.append({
                        "Baslangic": all_days[start_idx],
                        "Bitis": all_days[end_idx],
                        "Kullanilacak Izin": work_streak,
                        "Toplam Tatil": total_vacation,
                        "Verimlilik": round(total_vacation / work_streak if work_streak > 0 else total_vacation, 1),
                        "Sebep": ", ".join(holiday_names) if holiday_names else "Weekend"
                    })
            i = temp_i
        else:
            i += 1
    return pd.DataFrame(opportunities)

# ==========================================
# 3. ARAYUZ (FRONTEND)
# ==========================================

with st.sidebar:
    # --- DIL VE ULKE SECIMI ---
    # Varsayilan olarak US secili gelir -> Dil Ingilizce olur
    selected_code = st.selectbox("Select Country", options=list(COUNTRY_OPTIONS.keys()), format_func=lambda x: COUNTRY_OPTIONS[x])
    
    # Dil belirleme mantigi
    lang_code = "EN" # Varsayilan
    if selected_code == "TR": lang_code = "TR"
    elif selected_code == "DE": lang_code = "DE"
    elif selected_code == "PL": lang_code = "PL"
    
    T = TEXTS[lang_code] # Aktif dil sozlugu
    
    st.header(T["settings"])
    st.divider()

    # --- ALMANYA ICIN EYALET SECIMI ---
    selected_subdiv = None
    if selected_code == "DE":
        subdiv_code = st.selectbox(
            T["state"], 
            options=list(GERMAN_STATES.keys()),
            format_func=lambda x: GERMAN_STATES[x]
        )
        selected_subdiv = subdiv_code
    
    # Diger Ayarlar
    sel_year = st.number_input(T["year"], min_value=2024, max_value=2030, value=2026)
    
    default_start = date(sel_year, 1, 1)
    default_end = date(sel_year, 12, 31)
    
    date_range = st.date_input(
        T["date_range"],
        value=(default_start, default_end),
        min_value=default_start,
        max_value=default_end
    )
    
    st.divider()
    max_bridge = st.slider(T["max_bridge"], 1, 10, 2)
    
    calc_button = st.button(T["calc_btn"], type="primary", use_container_width=True)

# --- ANA EKRAN ---
st.title(T['title'])
st.markdown(T['desc'])

if calc_button:
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_d, end_d = date_range
        
        with st.spinner('...'):
            df = optimize_holidays(selected_code, start_d, end_d, max_bridge, subdiv=selected_subdiv)
        
        if not df.empty:
            # --- SIRALAMA MANTIĞI ---
            
            # 1. EN İYİ FIRSATI BUL (Verimlilik puanı en yüksek olan)
            best = df.sort_values(by=["Verimlilik", "Toplam Tatil"], ascending=False).iloc[0]

            # 2. LİSTEYİ TARİHE GÖRE SIRALA (Ocak -> Aralık)
            df = df.sort_values(by=["Baslangic"], ascending=True).reset_index(drop=True)

            # --- GÖRSELLEŞTİRME ---

            st.markdown(f"### {T['best_option']}")
            
            # 3'lu metrik kart yapisi
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""<div class="metric-card"><div class="metric-label">{T['leave_days']}</div><div class="metric-value">{best['Kullanilacak Izin']}</div></div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""<div class="metric-card"><div class="metric-label">{T['vacation_days']}</div><div class="metric-value">{best['Toplam Tatil']}</div></div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""<div class="metric-card"><div class="metric-label">{T['efficiency']}</div><div class="metric-value">{best['Verimlilik']}x</div></div>""", unsafe_allow_html=True)
            
            # Bilgilendirme (Emojisiz)
            st.success(f"**{T['reason']}:** {best['Sebep']} \n\n {best['Baslangic'].strftime('%d.%m.%Y')} - {best['Bitis'].strftime('%d.%m.%Y')}")
            
            st.write("---")
            st.subheader(f"{T['all_options']} ({len(df)})")
            
            for i, row in df.iterrows():
                efficiency_score = min(row['Verimlilik'] / 5.0, 1.0)
                start_str = row['Baslangic'].strftime("%Y-%m-%d")
                end_str = row['Bitis'].strftime("%Y-%m-%d")
                
                # Affiliate Link Yapisi
                flight_url = f"https://www.skyscanner.com.tr/transport/flights/{selected_code.lower()}/everywhere/{start_str}/{end_str}/"
                hotel_url = f"https://www.booking.com/searchresults.html?ss={COUNTRY_OPTIONS[selected_code]}&checkin={start_str}&checkout={end_str}"
                
                with st.expander(f"{row['Toplam Tatil']} Days ({row['Baslangic'].strftime('%d.%m')} - {row['Bitis'].strftime('%d.%m')})"):
                    st.write(f"**{T['leave_days']}:** {row['Kullanilacak Izin']}")
                    st.write(f"**{T['reason']}:** {row['Sebep']}")
                    st.progress(efficiency_score)
                    
                    st.markdown("---")
                    st.markdown(f"**{T['cta_text']}**")
                    col_ads1, col_ads2 = st.columns(2)
                    with col_ads1: st.link_button(T['check_flight'], flight_url, use_container_width=True)
                    with col_ads2: st.link_button(T['check_hotel'], hotel_url, use_container_width=True)
        else:
            st.warning(T['warn_no_result'])
    else:
        st.error(T['error_date'])
else:
    st.info(T['info_start'])