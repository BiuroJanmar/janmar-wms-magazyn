import streamlit as st
import random
from datetime import datetime

# Konfiguracja ekranu dla tabletu
st.set_page_config(page_title="Janmar WMS - Przyjęcie", page_icon="📦", layout="centered")

# ==============================================================================
# CSS - STYLIZACJA INTERFEJSU (WIELKIE PRZYCISKI, DUŻA CZCIONKA)
# ==============================================================================
st.markdown("""
    <style>
    html, body, [data-testid="stWidgetLabel"] p {
        font-size: 20px !important;
        font-weight: 600 !important;
    }
    .stButton>button {
        width: 100% !important;
        height: 70px !important;
        font-size: 22px !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
    }
    div[data-testid="stNumberInput"] input {
        font-size: 24px !important;
        height: 55px !important;
        font-weight: bold !important;
    }
    div[data-testid="stTextInput"] input {
        font-size: 22px !important;
        height: 55px !important;
    }
    .status-box {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 24px;
        color: white;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_unsafe_with_transparent_background=True, unsafe_allow_html=True)

# Tytuł systemu
st.title("🏭 JANMAR WMS - PANEL PRZYJĘCIA")
st.subheader("System rejestracji dostaw towaru na magazynie (v1.0 PROTOTYP)")
st.write("---")

# Symulacja bazy danych w pamięci sesji Streamlit
if "baza_dostawcow" not in st.session_state:
    st.session_state["baza_dostawcow"] = {
        "JAN-10023": {"nazwa": "AGRO-HURT JANUSZ", "tel": "601234567"},
        "JAN-10452": {"nazwa": "POL-FRUT SP. Z O.O.", "tel": "509876543"},
        "JAN-10891": {"nazwa": "GOSPODARSTWO GRZEGORZ", "tel": "785123456"}
    }

if "lista_towarow" not in st.session_state:
    st.session_state["lista_towarow"] = [
        "ARBUZ LUZ", "ZIEMNIAK WCZESNY LUZ", "ZIEMNIAK LUZ", 
        "KAPUSTA PEKIŃSKA LUZ", "KAPUSTA WŁOSKA LUZ", "KAPUSTA WŁOSKA SZT."
    ]

if "palety_tir" not in st.session_state:
    st.session_state["palety_tir"] = []

# ==============================================================================
# KROK 1: DOSTAWCA I DANE PODSTAWOWE
# ==============================================================================
st.header("1. Dane Dostawy i Kontrahenta")

automatyczna_data = datetime.today().strftime('%Y-%m-%d %H:%M')
st.info(f"📅 Data i godzina przyjęcia (Auto): **{automatyczna_data}**")

opcje_dostawcow = {k: f"{v['nazwa']} ({k})" for k, v in st.session_state["baza_dostawcow"].items()}
wybrany_id = st.selectbox("Wybierz dostawcę z bazy:", options=list(opcje_dostawcow.keys()), format_func=lambda x: opcje_dostawcow[x])

# Formularz dodawania nowego dostawcy
nowy_dostawca_chk = st.checkbox("➕ [ KLIKNIJ ] JEŚLI TO NOWY DOSTAWCA (SPOZA LISTY)")
if nowy_dostawca_chk:
    st.markdown("### 🆕 Rejestracja Nowego Dostawcy")
    nowa_nazwa = st.text_input("Pełna nazwa dostawcy / gospodarstwa:")
    nowy_tel = st.text_input("Numer telefonu komórkowego (wymagany - 9 cyfr):", max_chars=9)
    
    if st.button("💾 ZAPISZ DOSTAWCĘ W BAZIE"):
        if nowa_nazwa and len(nowy_tel) == 9 and nowy_tel.isdigit():
            wylosowane_id = f"JAN-{random.randint(11000, 99999)}"
            st.session_state["baza_dostawcow"][wylosowane_id] = {"nazwa": nowa_nazwa.upper(), "tel": nowy_tel}
            st.success(f"✅ Sukces! Nadano unikalny nik dostawcy: {wylosowane_id}. Możesz go teraz wybrać z listy powyżej.")
            st.rerun()
        else:
            st.error("❌ Błąd: Wpisz nazwę i poprawny 9-cyfrowy numer komórkowy!")

st.write("---")

# ==============================================================================
# KROK 2: ASORTYMENT
# ==============================================================================
st.header("2. Asortyment i Towar")

wybrany_towar = st.selectbox("Wybierz rodzaj towaru:", options=st.session_state["lista_towarow"])

nowy_towar_chk = st.checkbox("➕ [ KLIKNIJ ] DODAJ NOWY RODZAJ DO LISTY ASORTYMENTU")
if nowy_towar_chk:
    dodaj_towar_nazwa = st.text_input("Wpisz nowy asortyment (max 3 człony, np. MARCHEW LUZ):")
    if st.button("💾 ZAPISZ NOWY ASORTYMENT"):
        if dodaj_towar_nazwa:
            st.session_state["lista_towarow"].append(dodaj_towar_nazwa.upper())
            st.success(f"Dodano {dodaj_towar_nazwa.upper()} do listy.")
            st.rerun()

st.write("---")

# ==============================================================================
# KROK 3: OPAKOWANIA I PALETY
# ==============================================================================
st.header("3. Logika Opakowań i Sald")

rodzaj_opakowania = st.radio("Rodzaj opakowania towaru:", ["OPAKOWANIE JEDNORAZOWE", "OPAKOWANIE WYMIENNE"], index=0)

szczegoly_opakowania = ""
nr_opakowania_sieciowego = ""

if rodzaj_opakowania == "OPAKOWANIE WYMIENNE":
    st.markdown("#### 🔄 Szczegóły opakowania wymiennego")
    lista_wymiennych = [
        "KARTON POBRANY Z JANMAR", 
        "ŁUSZCZKA POBRANA JANMAR", 
        "SKRZYNIA POBRANA JANMAR", 
        "SKRZYNIA WŁASNOŚĆ DOSTAWCY", 
        "OPAKOWANIE IVCO", 
        "OPAKOWANIE EUROPUL"
    ]
    szczegoly_opakowania = st.selectbox("Wybierz typ opakowania wymiennego:", options=lista_wymiennych)
    
    if szczegoly_opakowania in ["OPAKOWANIE IVCO", "OPAKOWANIE EUROPUL"]:
        nr_opakowania_sieciowego = st.text_input(f"WPROWADŹ NUMER SERYJNY OPAKOWANIA {szczegoly_opakowania}:")

st.markdown("#### 🪵 Rodzaj palet")
rodzaj_palety = st.selectbox("Towar przyjechał na palecie:", ["PALETA EURO", "PALETA JEDNORAZOWA", "LUZEM (BEZ PALET)"])

st.write("---")

# ==============================================================================
# KROK 4: WAGI I TRYBY PRZYJĘCIA
# ==============================================================================
st.header("4. Rejestracja Ilości i Wag")

tryb_przyjecia = st.radio("Wybierz gabaryt dostawy:", ["SZYBKIE PRZYJĘCIE (Mała dostawa / Busy)", "ROZŁADUNEK TIR (Ważenie paletowe)"])

waga_netto_laczna = 0.0
ilosc_opakowan_laczna = 0
ilosc_szt_kg_laczna = 0.0

if tryb_przyjecia == "SZYBKIE PRZYJĘCIE (Mała dostawa / Busy)":
    st.markdown("### ⚡ Szybki formularz zbiorczy")
    ilosc_szt_kg_laczna = st.number_input("Łączna ilość towaru (Sztuki lub Kilogramy):", min_value=0.0, value=0.0, step=10.0)
    ilosc_opakowan_laczna = st.number_input("Łączna ilość skrzynek/opakowań (op.):", min_value=0, value=0, step=1)
    waga_netto_laczna = ilosc_szt_kg_laczna # Uproszczenie dla szybkich dostaw
    
else:
    st.markdown("### ⚖️ Sekwencyjne Ważenie Paletowe (TIR)")
    st.write("Wpisz dane dla każdej palety z osobna. System sam obliczy wagę Netto.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        waga_brutto_p = st.number_input("Waga BRUTTO palety (kg):", min_value=0.0, value=0.0)
    with col2:
        ilosc_op_p = st.number_input("Ilość skrzynek na tej palecie (szt):", min_value=0, value=0)
    with col3:
        waga_jednego_op = st.number_input("Waga samej skrzynki (tara - kg):", min_value=0.0, value=0.5, step=0.1)
        
    tara_palety_sztywna = 25.0 if rodzaj_palety == "PALETA EURO" else 15.0
    if rodzaj_palety == "LUZEM (BEZ PALET)": tara_palety_sztywna = 0.0
    
    tara_laczna_palety = tara_palety_sztywna + (ilosc_op_p * waga_jednego_op)
    netto_palety_wyliczone = max(0.0, waga_brutto_p - tara_laczna_palety)
    
    st.warning(f"🧮 Wyliczone NETTO dla tej palety: **{netto_palety_wyliczone} kg** (Odliczono: paleta {tara_palety_sztywna}kg + skrzynki {ilosc_op_p * waga_jednego_op}kg)")
    
    if st.button("➕ ZATWIERDŹ I ZWAŻ NASTĘPNĄ PALETĘ"):
        if waga_brutto_p > 0 and ilosc_op_p > 0:
            st.session_state["palety_tir"].append({
                "paleta_nr": len(st.session_state["palety_tir"]) + 1,
                "brutto": waga_brutto_p,
                "opakowania": ilosc_op_p,
                "tara": tara_laczna_palety,
                "netto": netto_palety_wyliczone
            })
            st.success(f"Dodano Paletę nr {len(st.session_state['palety_tir'])} do rejestru dostawy.")
            st.rerun()

    if st.session_state["palety_tir"]:
        st.markdown("#### 📊 Podsumowanie dotychczasowych palet z TIRA:")
        for p in st.session_state["palety_tir"]:
            st.text(f"Paleta {p['paleta_nr']}: Brutto: {p['brutto']}kg | Skrzynki: {p['opakowania']} szt | Netto: {p['netto']}kg")
            
        ilosc_opakowan_laczna = sum(p['opakowania'] for p in st.session_state["palety_tir"])
        waga_netto_laczna = sum(p['netto'] for p in st.session_state["palety_tir"])
        
        st.markdown(f"**RAZEM Z TIR-A:** Palet: `{len(st.session_state['palety_tir'])}` | Opakowań: `{ilosc_opakowan_laczna}` | Łączna waga NETTO: `{waga_netto_laczna} kg`")
        
        if st.button("🗑️ WYCZYŚĆ REJESTR PALET (RESET)"):
            st.session_state["palety_tir"] = []
            st.rerun()

st.write("---")

# ==============================================================================
# KROK 5: OCENA JAKOŚCIOWA (TRAFFIC LIGHTS)
# ==============================================================================
st.header("5. Ocena Jakościowa Towaru")
st.write("Kliknij odpowiedni status kontroli towaru:")

if "status_jakosci" not in st.session_state:
    st.session_state["status_jakosci"] = "NIEWYBRANY"

c1, c2, c3 = st.columns(3)
with c1:
    if st.button("🟢 TOWAR OK (PRZYJĘTY)"):
        st.session_state["status_jakosci"] = "ZIELONY"
with c2:
    if st.button("🟠 WARUNKOWY (KUPCIE)") :
        st.session_state["status_jakosci"] = "POMARAŃCZOWY"
with c3:
    if st.button("🔴 ZWROT TOVARU (100%)"):
        st.session_state["status_jakosci"] = "CZERWONY"

# Wyświetlanie wybranego statusu i dodatkowych opcji
if st.session_state["status_jakosci"] == "ZIELONY":
    st.markdown('<div class="status-box" style="background-color: #2ecc71;">🟢 JAKOŚĆ OK - TOWAR PRZYJĘTY</div>', unsafe_allow_html=True)
    komentarz_jakosc = "Towar zgodny z normami Janmar. Brak uwag jakościowych."
    
elif st.session_state["status_jakosci"] == "POMARAŃCZOWY":
    st.markdown('<div class="status-box" style="background-color: #f39c12;">🟠 PRZYJĘCIE WARUNKOWE</div>', unsafe_allow_html=True)
    
    opcje_pomaranczowe = [
        "TOWAR PRZYJĘTY WARUNKOWO DO ROZLICZENIA PO SPRZEDAŻY PRZEZ KUPCA",
        "UBYTEK WAGI POWYŻEJ TOLERANCJI",
        "WIDOCZNE USZKODZENIA MECHANICZNE / TRANSPORTOWE",
        "ODKŁOSY/OZNAKI PSUCIA – WYMAGA PRZEBRANIA NA MAGAZYNIE",
        "ZŁY KALIBRAŻ / NIEZGODNOŚĆ Z ZAMÓWIENIEM SIECI"
    ]
    szablon_komentarza = st.selectbox("Wybierz powód uchybienia:", options=opcje_pomaranczowe)
    opis_reczny = st.text_input("Dodatkowy opis wad (opcjonalnie):")
    komentarz_jakosc = f"WARUNKOWO: {szablon_komentarza}. Uproszczony opis: {opis_reczny}"

elif st.session_state["status_jakosci"] == "CZERWONY":
    st.markdown('<div class="status-box" style="background-color: #e74c3c;">🔴 TOWAR ODRZUCONY - ZWROT DO DOSTAWCY</div>', unsafe_allow_html=True)
    komentarz_jakosc = st.text_input("Wpisz uzasadnienie 100% zwrotu towaru (wymagane):")

st.write("---")

# ==============================================================================
# KROK 6: PODPIS I GENEROWANIE
# ==============================================================================
st.header("6. Autoryzacja i Zamknięcie Dokumentu PZ")

magazynier_imie = st.selectbox("Przyjmujący magazynier:", ["Jan Kowalski", "Mariusz Nowak", "Piotr Zieliński", "Krzysztof Głowacki"])

if st.button("🔒 ZATWIERDŹ DOSTAWĘ I GENERUJ DOKUMENT PZ"):
    if st.session_state["status_jakosci"] == "NIEWYBRANY":
        st.error("❌ Błąd! Musisz wybrać ocenę jakościową towaru (kliknij zielony, pomarańczowy lub czerwony kafel)!")
    elif tryb_przyjecia == "ROZŁADUNEK TIR (Ważenie paletowe)" and not st.session_state["palety_tir"]:
        st.error("❌ Błąd! Wybrałeś tryb TIR, ale nie zarejestrowałeś żadnej zważonej palety!")
    else:
        # Symulacja bazy i generowania dokumentu
        dane_dostawcy_koncowe = st.session_state["baza_dostawcow"][wybrany_id]
        
        st.success("🎉 DOKUMENT PZ WYGENEROWANY POMYŚLNIE!")
        st.balloons()
        
        # Ekran podsumowania dla kierownika/handlowca
        st.markdown("### 📋 PODSUMOWANIE RAPORTU PZ JANMAR")
        st.write(f"**Dostawca:** {dane_dostawcy_koncowe['nazwa']} | **ID:** {wybrany_id} | **Telefon:** {dane_dostawcy_koncowe['tel']}")
        st.write(f"**Asortyment:** {wybrany_towar} | **Opakowanie:** {rodzaj_opakowania} {szczegoly_opakowania} {nr_opakowania_sieciowego}")
        st.write(f"**Logistyka:** {rodzaj_palety} | **Łączna ilość skrzynek:** {ilosc_opakowan_laczna} op.")
        st.write(f"**Waga Netto Dostawy:** {waga_netto_laczna} kg / szt.")
        st.write(f"**Status Jakości:** {st.session_state['status_jakosci']} ({komentarz_jakosc})")
        st.write(f"**Dokument sporządził:** {magazynier_imie}")
        
        st.info("📲 W Etapie 2 podepniemy tutaj skrypt wysyłający ten raport automatycznym SMS-em/WhatsAppem na numer dostawcy oraz zapisujący rekord do stałej bazy danych sieci handlowców Janmar.")
