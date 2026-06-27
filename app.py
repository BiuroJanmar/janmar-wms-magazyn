import streamlit as st
import random
from datetime import datetime

# Konfiguracja ekranu dla tabletu
st.set_page_config(page_title="Janmar WMS - Przyjęcie", page_icon="📦", layout="centered")

# CSS - Wielkie przyciski pod palec, duża czcionka dla magazynu
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
""", unsafe_allow_html=True)

st.title("🏭 JANMAR WMS - PANEL PRZYJĘCIA")
st.subheader("ETAP 1: Testy interfejsu dotykowego na magazynie (v1.3)")
st.write("---")

# Baza w pamięci sesji (do testów klikania)
if "baza_dostawcow" not in st.session_state:
    st.session_state["baza_dostawcow"] = {
        "JAN-10023": {"nazwa": "AGRO-HURT JANUSZ", "tel": "601234567"},
        "JAN-10452": {"nazwa": "POL-FRUT SP. Z O.O.", "tel": "509876543"}
    }
if "lista_towarow" not in st.session_state:
    st.session_state["lista_towarow"] = ["ARBUZ LUZ", "ZIEMNIAK WCZESNY LUZ", "ZIEMNIAK LUZ", "KAPUSTA PEKIŃSKA LUZ", "KAPUSTA WŁOSKA LUZ"]
if "palety_tir" not in st.session_state:
    st.session_state["palety_tir"] = []

# --- KROK 1: DOSTAWCA ---
st.header("1. Dane Dostawy i Kontrahenta")
automatyczna_data = datetime.today().strftime('%Y-%m-%d %H:%M')
st.info(f"📅 Data i godzina przyjęcia (Auto): **{automatyczna_data}**")

opcje_dostawcow = {k: f"{v['nazwa']} ({k})" for k, v in st.session_state["baza_dostawcow"].items()}
wybrany_id = st.selectbox("Wybierz dostawcę z bazy:", options=list(opcje_dostawcow.keys()), format_func=lambda x: opcje_dostawcow[x])

nowy_dostawca_chk = st.checkbox("➕ [ KLIKNIJ ] JEŚLI TO NOWY DOSTAWCA (SPOZA LISTY)")
if nowy_dostawca_chk:
    st.markdown("### 🆕 Rejestracja Nowego Dostawcy")
    nowa_nazwa = st.text_input("Pełna nazwa dostawcy / gospodarstwa:")
    nowy_tel = st.text_input("Numer telefonu komórkowego (wymagany - 9 cyfr):", max_chars=9)
    if st.button("💾 ZAPISZ DOSTAWCĘ W BAZIE"):
        if nowa_nazwa and len(nowy_tel) == 9 and nowy_tel.isdigit():
            wylosowane_id = f"JAN-{random.randint(11000, 99999)}"
            st.session_state["baza_dostawcow"][wylosowane_id] = {"nazwa": nowa_nazwa.upper(), "tel": nowy_tel}
            st.success(f"✅ Nadano ID: {wylosowane_id}. Wybierz go z listy powyżej.")
            st.rerun()

st.write("---")

# --- KROK 2: ASORTYMENT ---
st.header("2. Asortyment i Opakowania")
wybrany_towar = st.selectbox("Wybierz rodzaj towaru:", options=st.session_state["lista_towarow"])

nowy_towar_chk = st.checkbox("➕ [ KLIKNIJ ] DODAJ NOWY RODZAJ DO LISTY ASORTYMENTU")
if nowy_towar_chk:
    dodaj_towar_nazwa = st.text_input("Wpisz nowy asortyment:")
    if st.button("💾 ZAPISZ NOWY ASORTYMENT"):
        if dodaj_towar_nazwa:
            st.session_state["lista_towarow"].append(dodaj_towar_nazwa.upper())
            st.rerun()

rodzaj_opakowania = st.radio("Rodzaj opakowania towaru:", ["OPAKOWANIE JEDNORAZOWE", "OPAKOWANIE WYMIENNE"])
szczegoly_opakowania = ""
nr_opakowania_sieciowego = ""
if rodzaj_opakowania == "OPAKOWANIE WYMIENNE":
    szczegoly_opakowania = st.selectbox("Wybierz typ opakowania wymiennego:", options=["KARTON JANMAR", "ŁUSZCZKA JANMAR", "SKRZYNIA JANMAR", "WŁASNOŚĆ DOSTAWCY", "OPAKOWANIE IVCO", "OPAKOWANIE EUROPUL"])
    if szczegoly_opakowania in ["OPAKOWANIE IVCO", "OPAKOWANIE EUROPUL"]:
        nr_opakowania_sieciowego = st.text_input(f"WPROWADŹ NUMER SERYJNY OPAKOWANIA {szczegoly_opakowania}:")

rodzaj_palety = st.selectbox("Towar przyjechał na palecie:", ["PALETA EURO", "PALETA JEDNORAZOWA", "LUZEM (BEZ PALET)"])
st.write("---")

# --- KROK 3: WAGI I SALDA ---
st.header("3. Rejestracja Ilości i Wag")
tryb_przyjecia = st.radio("Wybierz gabaryt dostawy:", ["SZYBKIE PRZYJĘCIE (Mała dostawa / Busy)", "ROZŁADUNEK TIR (Ważenie paletowe)"])

waga_netto_laczna = 0.0
ilosc_opakowan_laczna = 0
ilosc_palet_dostarczonych = 0

if tryb_przyjecia == "SZYBKIE PRZYJĘCIE (Mała dostawa / Busy)":
    st.markdown("### ⚡ Szybki formularz zbiorczy")
    ilosc_szt_kg_laczna = st.number_input("Łączna ilość towaru (Sztuki lub Kilogramy):", min_value=0.0, value=0.0)
    ilosc_opakowan_laczna = st.number_input("Ilość dostarczonych skrzynek (z towarem):", min_value=0, value=0)
    ilosc_palet_dostarczonych = st.number_input("Ilość dostarczonych palet (z towarem):", min_value=0, value=0)
    waga_netto_laczna = ilosc_szt_kg_laczna
else:
    st.markdown("### ⚖️ Sekwencyjne Ważenie Paletowe (TIR)")
    col1, col2, col3 = st.columns(3)
    with col1: waga_brutto_p = st.number_input("Waga BRUTTO palety (kg):", min_value=0.0, value=0.0)
    with col2: ilosc_op_p = st.number_input("Ilość skrzynek na tej palecie (szt):", min_value=0, value=0)
    with col3: waga_jednego_op = st.number_input("Waga skrzynki (tara - kg):", min_value=0.0, value=0.5, step=0.1)
    
    tara_palety_sztywna = 25.0 if rodzaj_palety == "PALETA EURO" else 15.0
    if rodzaj_palety == "LUZEM (BEZ PALET)": tara_palety_sztywna = 0.0
    tara_laczna_palety = tara_palety_sztywna + (ilosc_op_p * waga_jednego_op)
    netto_palety_wyliczone = max(0.0, waga_brutto_p - tara_laczna_palety)
    
    st.warning(f"🧮 Wyliczone NETTO dla tej palety: **{netto_palety_wyliczone} kg**")
    if st.button("➕ ZATWIERDŹ I ZWAŻ NASTĘPNĄ PALETĘ"):
        if waga_brutto_p > 0 and ilosc_op_p > 0:
            st.session_state["palety_tir"].append({"paleta_nr": len(st.session_state["palety_tir"]) + 1, "brutto": waga_brutto_p, "opakowania": ilosc_op_p, "netto": netto_palety_wyliczone})
            st.rerun()

    if st.session_state["palety_tir"]:
        for p in st.session_state["palety_tir"]:
            st.text(f"Paleta {p['paleta_nr']}: Brutto: {p['brutto']}kg | Skrzynki: {p['opakowania']} szt | Netto: {p['netto']}kg")
        ilosc_opakowan_laczna = sum(p['opakowania'] for p in st.session_state["palety_tir"])
        waga_netto_laczna = sum(p['netto'] for p in st.session_state["palety_tir"])
        ilosc_palet_dostarczonych = len(st.session_state["palety_tir"])
        st.markdown(f"**RAZEM Z TIR-A:** Palet: `{ilosc_palet_dostarczonych}` | Opakowań: `{ilosc_opakowan_laczna}` | NETTO: `{waga_netto_laczna} kg`")
        if st.button("🗑️ RESETUJ PALETY"):
            st.session_state["palety_tir"] = []
            st.rerun()

st.markdown("### 🔄 Saldo Opakowań i Palet (Wydawka)")
ilosc_opakowan_pobranych = 0
ilosc_palet_pobranych = 0
col_op, col_pal = st.columns(2)
with col_op:
    nie_op = st.checkbox("✅ NIE POBIERA OPAKOWAŃ", value=True)
    if not nie_op: ilosc_opakowan_pobranych = st.number_input("Ilość POBRANYCH skrzynek:", min_value=0, value=0)
with col_pal:
    nie_pal = st.checkbox("✅ NIE POBIERA PALET", value=True)
    if not nie_pal: ilosc_palet_pobranych = st.number_input("Ilość POBRANYCH palet:", min_value=0, value=0)

st.write("---")

# --- KROK 4: JAKOŚĆ ---
st.header("4. Ocena Jakościowa Towaru")
if "status_jakosci" not in st.session_state: st.session_state["status_jakosci"] = "NIEWYBRANY"

c1, c2, c3 = st.columns(3)
with c1:
    if st.button("🟢 TOWAR OK (PRZYJĘTY)"): st.session_state["status_jakosci"] = "ZIELONY"
with c2:
    if st.button("🟠 WARUNKOWY (KUPCIE)"): st.session_state["status_jakosci"] = "POMARAŃCZOWY"
with c3:
    if st.button("🔴 ZWROT TOWARU (100%)"): st.session_state["status_jakosci"] = "CZERWONY"

komentarz_jakosc = ""
if st.session_state["status_jakosci"] == "ZIELONY":
    st.markdown('<div class="status-box" style="background-color: #2ecc71;">🟢 JAKOŚĆ OK - TOWAR PRZYJĘTY</div>', unsafe_allow_html=True)
elif st.session_state["status_jakosci"] == "POMARAŃCZOWY":
    st.markdown('<div class="status-box" style="background-color: #f39c12;">🟠 PRZYJĘCIE WARUNKOWE</div>', unsafe_allow_html=True)
    komentarz_jakosc = st.selectbox("Powód:", ["TOWAR PRZYJĘTY WARUNKOWO DO ROZLICZENIA PO SPRZEDAŻY PRZEZ KUPCA", "UBYTEK WAGI POWYŻEJ TOLERANCJI", "WIDOCZNE USZKODZENIA MECHANICZNE / TRANSPORTOWE", "ODKŁOSY/OZNAKI PSUCIA – WYMAGA PRZEBRANIA NA MAGAZYNIE"])
elif st.session_state["status_jakosci"] == "CZERWONY":
    st.markdown('<div class="status-box" style="background-color: #e74c3c;">🔴 TOWAR ODRZUCONY - ZWROT</div>', unsafe_allow_html=True)
    komentarz_jakosc = st.text_input("Uzasadnienie zwrotu:")

st.write("---")

# --- KROK 5: ZATWIERDZENIE ORAZ DOSKOKI ---
st.header("5. Zamknięcie i Autoryzacja Dostawy")
magazynier_wybor = st.selectbox("Przyjmujący magazynier:", ["Jan Kowalski", "Mariusz Nowak", "Piotr Zieliński", "➕ INNA OSOBA (WPISZ RĘCZNIE)"])

magazynier_imie = ""
if magazynier_wybor == "➕ INNA OSOBA (WPISZ RĘCZNIE)":
    magazynier_imie = st.text_input("Wpisz imię i nazwisko osoby przyjmującej:").strip()
else:
    magazynier_imie = magazynier_wybor

if st.button("🔒 ZATWIERDŹ TESTOWE PRZYJĘCIE"):
    if st.session_state["status_jakosci"] == "NIEWYBRANY":
        st.error("❌ Musisz wybrać ocenę jakościową (Zielony/Pomarańczowy/Czerwony kafel)!")
    elif not magazynier_imie:
        st.error("❌ Podaj imię i nazwisko!")
    else:
        st.success(f"🎉 Sukces! Test zakończony pomyślnie dla magazyniera: {magazynier_imie}")
        st.write(f"**Towar:** {wybrany_towar} | **Netto:** {waga_netto_laczna} kg")
        st.write(f"**Opakowania saldo:** Przywiózł {ilosc_opakowan_laczna} | Pobrał {ilosc_opakowan_pobranych}")
        st.write(f"**Palety saldo:** Przywiózł {ilosc_palet_dostarczonych} | Pobrał {ilosc_palet_pobranych}")
