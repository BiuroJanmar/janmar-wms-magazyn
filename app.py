import streamlit as st
import random
import urllib.parse
from datetime import datetime
from io import BytesIO

# Importy do generowania profesjonalnego PDF z tabelami
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Konfiguracja ekranu pod tablet
st.set_page_config(page_title="Janmar WMS - Przyjęcie", page_icon="📦", layout="centered")

# CSS - Wielkie przyciski i czcionki pod palec na magazyn
st.markdown("""
    <style>
    html, body, [data-testid="stWidgetLabel"] p { font-size: 20px !important; font-weight: 600 !important; }
    .stButton>button { width: 100% !important; height: 70px !important; font-size: 22px !important; font-weight: bold !important; border-radius: 12px !important; margin-bottom: 10px !important; }
    div[data-testid="stNumberInput"] input { font-size: 24px !important; height: 55px !important; font-weight: bold !important; }
    div[data-testid="stTextInput"] input { font-size: 22px !important; height: 55px !important; }
    .status-box { padding: 20px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 24px; color: white; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.title("🏭 JANMAR WMS - PANEL PRZYJĘCIA v2.2 🔒")
st.subheader("Pełny system: Rejestracja wag, Salda, PDF i WhatsApp")
st.write("---")

# Bazy danych w pamięci sesji
if "baza_dostawcow" not in st.session_state:
    st.session_state["baza_dostawcow"] = {
        "JAN-10023": {"nazwa": "AGRO-HURT JANUSZ", "tel": "601234567"},
        "JAN-10452": {"nazwa": "POL-FRUT SP. Z O.O.", "tel": "509876543"},
        "JAN-10891": {"nazwa": "GOSPODARSTWO GRZEGORZ", "tel": "785123456"}
    }
if "lista_towarow" not in st.session_state:
    st.session_state["lista_towarow"] = ["ARBUZ LUZ", "ZIEMNIAK WCZESNY LUZ", "ZIEMNIAK LUZ", "KAPUSTA PEKIŃSKA LUZ", "KAPUSTA WŁOSKA LUZ", "KAPUSTA WŁOSKA SZT."]
if "palety_tir" not in st.session_state:
    st.session_state["palety_tir"] = []

# FUNKCJA GENERUJĄCA FORMALNY DOKUMENT PDF PZ
def generuj_pdf_pz(nr_pz, data, dostawca_id, dostawca_dane, towar, opakowanie_str, paleta_str, przywiezione_op, pobrane_op, przywiezione_pal, pobrane_pal, netto, status, uwagi, osoba_prow):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottom=30)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=22, leading=26, textColor=colors.HexColor('#1F497D'), alignment=1)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=11, leading=15, textColor=colors.black)
    bold_style = ParagraphStyle('BoldStyle', parent=styles['Normal'], fontSize=12, leading=16, fontName='Helvetica-Bold')
    
    story.append(Paragraph(f"<b>DOKUMENT PZ - PRZYJĘCIE ZEWNĘTRZNE nr: {nr_pz}</b>", title_style))
    story.append(Spacer(1, 15))
    
    status_kolor = '#2ecc71' if status == 'ZIELONY' else ('#f39c12' if status == 'POMARAŃCZOWY' else '#e74c3c')
    
    dane_ogolne = [
        [Paragraph(f"<b>Nabywca / Magazyn:</b><br/>GPW JANMAR SP. Z O.O. SP. K.<br/>ul. Gołaśka 3/58, Kraków", sub_style),
         Paragraph(f"<b>Dostawca:</b><br/>{dostawca_dane['nazwa']}<br/>ID: {dostawca_id}<br/>Tel: {dostawca_dane['tel']}", sub_style)],
        [Paragraph(f"<b>Data dostawy:</b> {data}<br/><b>Sporządził:</b> {osoba_prow}", sub_style),
         Paragraph(f"<font color='{status_kolor}'><b>STATUS JAKOŚCI: {status}</b></font><br/>Uwag/Opis: {uwagi}", sub_style)]
    ]
    
    t_ogolne = Table(dane_ogolne, colWidths=[270, 270])
    t_ogolne.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F2F5F8')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#1F497D')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D9D9D9')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_ogolne)
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("<b>SPECYFIKACJA ILOŚCIOWO-WAGOWA ORAZ SALDO OPAKOWAŃ</b>", bold_style))
    story.append(Spacer(1, 8))
    
    tabela_towarowa = [
        ["Parametr rozliczeniowy", "Dostarczono (Wjazd)", "Pobrano (Wyjazd)", "Saldo Końcowe"],
        [f"Towar: {towar}", f"{netto} kg / szt.", "-", f"{netto} kg / szt."],
        [f"Opakowania ({opakowanie_str})", f"{przywiezione_op} op.", f"{pobrane_op} op.", f"{przywiezione_op - pobrane_op} op."],
        [f"Palety ({paleta_str})", f"{przywiezione_pal} szt.", f"{pobrane_pal} szt.", f"{przywiezione_pal - pobrane_pal} szt."]
    ]
    
    t_towarowa = Table(tabela_towarowa, colWidths=[200, 110, 110, 120])
    t_towarowa.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1F497D')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#1F497D')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D9D9D9')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_towarowa)
    story.append(Spacer(1, 45))
    
    story.append(Paragraph(f"...........................................................<br/>Podpis Magazyniera Zmianowego ({osoba_prow})", sub_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ==============================================================================
# KROK 1: DOSTAWCA
# ==============================================================================
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
            st.success(f"✅ Nadano unikalny nik: {wylosowane_id}. Wybierz go z listy powyżej.")
            st.rerun()

st.write("---")

# ==============================================================================
# KROK 2 & 3: TOWAR I LOGIKA OPAKOWAŃ
# ==============================================================================
st.header("2. Asortyment i Opakowania")
wybrany_towar = st.selectbox("Wybierz rodzaj towaru:", options=st.session_state["lista_towarow"])

nowy_towar_chk = st.checkbox("➕ [ KLIKNIJ ] DODAJ NOWY RODZAJ DO LISTY ASORTYMENTU")
if nowy_towar_chk:
    dodaj_towar_nazwa = st.text_input("Wpisz nowy asortyment (np. MARCHEW LUZ):")
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

# ==============================================================================
# KROK 4: WAGI, TRYBY I SALDA (PRZYWÓZ VS WYDAWKA)
# ==============================================================================
st.header("3. Rejestracja Ilości i Wag")
tryb_przyjecia = st.radio("Wybierz gabaryt dostawy:", ["SZYBKIE PRZYJĘCIE (Mała dostawa / Busy)", "ROZŁADUNEK TIR (Ważenie paletowe)"])

waga_netto_laczna = 0.0
ilosc_opakowan_laczna = 0
ilosc_palet_dostarczonych = 0

if tryb_przyjecia == "SZYBKIE PRZYJĘCIE (Mała dostawa / Busy)":
    st.markdown("### ⚡ Szybki formularz zbiorczy (Dostawa)")
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
        st.markdown("#### 📊 Zarejestrowane palety:")
        for p in st.session_state["palety_tir"]:
            st.text(f"Paleta {p['paleta_nr']}: Brutto: {p['brutto']}kg | Skrzynki: {p['opakowania']} szt | Netto: {p['netto']}kg")
        ilosc_opakowan_laczna = sum(p['opakowania'] for p in st.session_state["palety_tir"])
        waga_netto_laczna = sum(p['netto'] for p in st.session_state["palety_tir"])
        ilosc_palet_dostarczonych = len(st.session_state["palety_tir"])
        st.markdown(f"**RAZEM Z TIR-A:** Palet: `{ilosc_palet_dostarczonych}` | Opakowań: `{ilosc_opakowan_laczna}` | NETTO: `{waga_netto_laczna} kg`")
        if st.button("🗑️ RESETUJ PALETY"):
            st.session_state["palety_tir"] = []
            st.rerun()

st.markdown("### 🔄 Saldo Opakowań i Palet (Wydawka/Pobranie)")
ilosc_opakowan_pobranych = 0
ilosc_palet_pobranych = 0
col_op, col_pal = st.columns(2)
with col_op:
    nie_op = st.checkbox("✅ NIE POBIERA OPAKOWAŃ", value=True)
    if not nie_op: ilosc_opakowan_pobranych = st.number_input("Ilość POBRANYCH pustych skrzynek (szt):", min_value=0, value=0)
with col_pal:
    nie_pal = st.checkbox("✅ NIE POBIERA PALET", value=True)
    if not nie_pal: ilosc_palet_pobranych = st.number_input("Ilość POBRANYCH pustych palet (szt):", min_value=0, value=0)

st.write("---")

# ==============================================================================
# KROK 4: SYSTEM JAKOŚCIOWY (TRAFFIC LIGHTS)
# ==============================================================================
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
    komentarz_jakosc = "Towar zgodny z normami jakościowymi."
elif st.session_state["status_jakosci"] == "POMARAŃCZOWY":
    st.markdown('<div class="status-box" style="background-color: #f39c12;">🟠 PRZYJĘCIE WARUNKOWE</div>', unsafe_allow_html=True)
    szablon = st.selectbox("Powód uchybienia:", ["TOWAR PRZYJĘTY WARUNKOWO DO ROZLICZENIA PO SPRZEDAŻY PRZEZ KUPCA", "UBYTEK WAGI POWYŻEJ TOLERANCJI", "WIDOCZNE USZKODZENIA MECHANICZNE / TRANSPORTOWE", "ODKŁOSY/OZNAKI PSUCIA – WYMAGA PRZEBRANIA NA MAGAZYNIE", "ZŁY KALIBRAŻ / NIEZGODNOŚĆ Z ZAMÓWIENIEM"])
    opis_reczny = st.text_input("Dodatkowy opis wad (opcjonalnie):")
    komentarz_jakosc = f"WARUNKOWO: {szablon}. Opis: {opis_reczny}"
elif st.session_state["status_jakosci"] == "CZERWONY":
    st.markdown('<div class="status-box" style="background-color: #e74c3c;">🔴 TOWAR ODRZUCONY - ZWROT DO DOSTAWCY</div>', unsafe_allow_html=True)
    komentarz_jakosc = st.text_input("Uzasadnienie 100% zwrotu (wymagane):")

st.write("---")

# ==============================================================================
# KROK 5: ZAMKNIĘCIE, ELASTYCZNY MAGAZYNIER I WYJŚCIE PDF/WHATSAPP
# ==============================================================================
st.header("5. Zamknięcie i Autoryzacja Dostawy")
magazynier_wybor = st.selectbox("Przyjmujący magazynier:", ["Jan Kowalski", "Mariusz Nowak", "Piotr Zieliński", "➕ INNA OSOBA (WPISZ RĘCZNIE)"])

magazynier_imie = ""
if magazynier_wybor == "➕ INNA OSOBA (WPISZ RĘCZNIE)":
    magazynier_imie = st.text_input("Wpisz imię i nazwisko osoby przyjmującej (Wymagane):").strip()
else:
    magazynier_imie = magazynier_wybor

if st.button("🔒 ZATWIERDŹ DOSTAWĘ I GENERUJ PDF + LINK WHATSAPP"):
    if st.session_state["status_jakosci"] == "NIEWYBRANY":
        st.error("❌ Musisz wybrać ocenę jakościową towaru!")
    elif not magazynier_imie:
        st.error("❌ Musisz podać imię i nazwisko osoby przyjmującej!")
    elif tryb_przyjecia == "ROZŁADUNEK TIR (Ważenie paletowe)" and not st.session_state["palety_tir"]:
        st.error("❌ Brak zarejestrowanych palet dla trybu TIR!")
    else:
        dane_d_koncowe = st.session_state["baza_dostawcow"][wybrany_id]
        losowy_nr_pz = f"PZ/{random.randint(10000,99999)}/{datetime.today().strftime('%Y')}"
        
        pdf_data = generuj_pdf_pz(
            losowy_nr_pz, automatyczna_data, wybrany_id, dane_d_koncowe, wybrany_towar,
            f"{rodzaj_opakowania} {szczegoly_opakowania} {nr_opakowania_sieciowego}", rodzaj_palety,
            ilosc_opakowan_laczna, ilosc_opakowan_pobranych, ilosc_palet_dostarczonych, ilosc_palet_pobranych,
            waga_netto_laczna, st.session_state["status_jakosci"], komentarz_jakosc, magazynier_imie
        )
        
        st.success("🎉 DOSTAWĘ ZAPISANO POMYŚLNIE W SYSTEMIE JANMAR!")
        st.balloons()
        
        st.download_button(
            label="📥 POBIERZ DOKUMENT PZ (PDF)",
            data=pdf_data,
            file_name=f"PZ_{wybrany_id}_{datetime.today().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )
        
        tekst_wiadomosci = (
            f"Dzień dobry, Firma JANMAR zarejestrowała dostawę towaru:\n"
            f"Dokument: {losowy_nr_pz}\n"
            f"Towar: {wybrany_towar}\n"
            f"Ilość: {waga_netto_laczna} kg / szt.\n"
            f"Saldo opakowań: {ilosc_opakowan_laczna - ilosc_opakowan_pobranych} op.\n"
            f"Saldo palet: {ilosc_palet_dostarczonych - ilosc_palet_pobranych} szt.\n"
            f"Status kontroli jakości: {st.session_state['status_jakosci']}\n"
            f"({komentarz_jakosc})\n"
            f"Dokument wystawił: {magazynier_imie}\n"
            f"Dziękujemy za dostawę!"
        )
        
        wiadomosc_url = urllib.parse.quote(tekst_wiadomosci)
        link_whatsapp = f"https://wa.me/48{dane_d_koncowe['tel']}?text={wiadomosc_url}"
        
        st.markdown("### 📲 Szybka Wysyłka Raportu na Telefon Dostawcy")
        st.markdown(f'<a href="{link_whatsapp}" target="_blank"><button style="width:100%; height:70px; background-color:#25D366; color:white; font-size:22px; font-weight:bold; border:none; border-radius:12px; cursor:pointer;">🟢 WYŚLIJ RAPORT DOSTAWY PRZEZ WHATSAPP</button></a>', unsafe_allow_html=True)
