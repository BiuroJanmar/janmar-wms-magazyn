import streamlit as st
import random
from datetime import datetime
from io import BytesIO
from streamlit_drawable_canvas import st_canvas

# Importy do generowania PDF z podpisem
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect

# Konfiguracja ekranu pod tablet
st.set_page_config(page_title="Janmar WMS - Przyjęcie", page_icon="📦", layout="centered")

# CSS - Wielkie przyciski pod palec
st.markdown("""
    <style>
    html, body, [data-testid="stWidgetLabel"] p { font-size: 20px !important; font-weight: 600 !important; }
    .stButton>button { width: 100% !important; height: 70px !important; font-size: 22px !important; font-weight: bold !important; border-radius: 12px !important; margin-bottom: 10px !important; }
    div[data-testid="stNumberInput"] input { font-size: 24px !important; height: 55px !important; font-weight: bold !important; }
    div[data-testid="stTextInput"] input { font-size: 22px !important; height: 55px !important; }
    .status-box { padding: 20px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 24px; color: white; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.title("🏭 JANMAR WMS - PANEL PRZYJĘCIA v1.5")
st.subheader("System magazynowy z podpisem dostawcy na ekranie")
st.write("---")

# Pamięć sesji
if "baza_dostawcow" not in st.session_state:
    st.session_state["baza_dostawcow"] = {
        "JAN-11199": {"nazwa": "MARCIN PRZEWORSKI", "tel": "601234567"},
        "JAN-10023": {"nazwa": "AGRO-HURT JANUSZ", "tel": "601234567"},
        "JAN-10452": {"nazwa": "POL-FRUT SP. Z O.O.", "tel": "509876543"}
    }
if "lista_towarow" not in st.session_state:
    st.session_state["lista_towarow"] = ["ARBUZ LUZ", "ZIEMNIAK WCZESNY LUZ", "ZIEMNIAK LUZ", "KAPUSTA PEKIŃSKA LUZ", "KAPUSTA WŁOSKA LUZ"]
if "palety_tir" not in st.session_state:
    st.session_state["palety_tir"] = []
if "lista_magazynierow" not in st.session_state:
    st.session_state["lista_magazynierow"] = ["Zbigniew Tkaczyk", "Jan Kowalski", "Mariusz Nowak", "Piotr Zieliński"]

# GENERATOR PDF
def generuj_pdf_pz(nr_pz, data, dostawca_id, dostawca_dane, towar, opakowanie_str, paleta_str, przywiezione_op, pobrane_op, przywiezione_pal, pobrane_pal, netto, status, uwagi, osoba_prow, podpis_img):
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
         Paragraph(f"<b>Dostawca:</b><br/>{dostawca_dane['nazwa']}<br/>ID: {dostawca_id}", sub_style)],
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
    story.append(Spacer(1, 30))
    
    # Podpisy (Magazynier oraz Wklejony Podpis Dostawcy)
    podpis_kierowcy_io = BytesIO()
    podpis_img.save(podpis_kierowcy_io, format='PNG')
    podpis_kierowcy_io.seek(0)
    
    img_reportlab = Image(podpis_kierowcy_io, width=120, height=50)
    
    tabela_podpisow = [
        [Paragraph(f"<b>Podpis Magazyniera Janmar:</b><br/><br/>............................................<br/>{osoba_prow}", sub_style),
         Paragraph("<b>Podpisano Cyfrowo przez Dostawcę:</b>", sub_style), img_reportlab]
    ]
    t_podpisy = Table(tabela_podpisow, colWidths=[240, 180, 120])
    t_podpisy.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'BOTTOM')]))
    
    story.append(t_podpisy)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# KROK 1: DOSTAWCA
st.header("1. Dane Dostawy i Kontrahenta")
automatyczna_data = datetime.today().strftime('%Y-%m-%d %H:%M')
st.info(f"📅 Data i godzina przyjęcia (Auto): **{automatyczna_data}**")

opcje_dostawcow = {k: f"{v['nazwa']} ({k})" for k, v in st.session_state["baza_dostawcow"].items()}
wybrany_id = st.selectbox("Wybierz dostawcę z bazy:", options=list(opcje_dostawcow.keys()), format_func=lambda x: opcje_dostawcow[x])

nowy_dostawca_chk = st.checkbox("➕ [ KLIKNIJ ] JEŚLI TO NOWY DOSTAWCA (SPOZA LISTY)")
if nowy_dostawca_chk:
    nowa_nazwa = st.text_input("Pełna nazwa dostawcy / gospodarstwa:")
    nowy_tel = st.text_input("Numer telefonu komórkowego (9 cyfr):", max_chars=9)
    if st.button("💾 ZAPISZ DOSTAWCĘ W BAZIE"):
        if nowa_nazwa and len(nowy_tel) == 9 and nowy_tel.isdigit():
            wylosowane_id = f"JAN-{random.randint(11000, 99999)}"
            st.session_state["baza_dostawcow"][wylosowane_id] = {"nazwa": nowa_nazwa.upper(), "tel": nowy_tel}
            st.success("✅ Dodano. Wybierz z listy powyżej.")
            st.rerun()

st.write("---")

# KROK 2: ASORTYMENT
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
        nr_opakowania_sieciowego = st.text_input(f"WPROWADŹ NUMER SERYJNY OPAKOWANIA:")

rodzaj_palety = st.selectbox("Towar przyjechał na palecie:", ["PALETA EURO", "PALETA JEDNORAZOWA", "LUZEM (BEZ PALET)"])
st.write("---")

# KROK 3: WAGI I SALDA
st.header("3. Rejestracja Ilości i Wag")
tryb_przyjecia = st.radio("Wybierz gabaryt dostawy:", ["SZYBKIE PRZYJĘCIE (Mała dostawa / Busy)", "ROZŁADUNEK TIR (Ważenie paletowe)"])

waga_netto_laczna = 0.0
ilosc_opakowan_laczna = 0
ilosc_palet_dostarczonych = 0

if tryb_przyjecia == "SZYBKIE PRZYJĘCIE (Mała dostawa / Busy)":
    ilosc_szt_kg_laczna = st.number_input("Łączna ilość towaru:", min_value=0.0, value=0.0)
    ilosc_opakowan_laczna = st.number_input("Ilość dostarczonych skrzynek:", min_value=0, value=0)
    ilosc_palet_dostarczonych = st.number_input("Ilość dostarczonych palet:", min_value=0, value=0)
    waga_netto_laczna = ilosc_szt_kg_laczna
else:
    col1, col2, col3 = st.columns(3)
    with col1: waga_brutto_p = st.number_input("Waga BRUTTO palety (kg):", min_value=0.0, value=0.0)
    with col2: ilosc_op_p = st.number_input("Ilość skrzynek na palecie (szt):", min_value=0, value=0)
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
            st.text(f"Paleta {p['paleta_nr']}: Brutto: {p['brutto']}kg | Netto: {p['netto']}kg")
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

# KROK 4: JAKOŚĆ
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
    komentarz_jakosc = "Towar zgodny z normami."
elif st.session_state["status_jakosci"] == "POMARAŃCZOWY":
    st.markdown('<div class="status-box" style="background-color: #f39c12;">🟠 PRZYJĘCIE WARUNKOWE</div>', unsafe_allow_html=True)
    komentarz_jakosc = st.selectbox("Powód:", ["TOWAR PRZYJĘTY WARUNKOWO DO ROZLICZENIA PO SPRZEDAŻY PRZEZ KUPCA", "UBYTEK WAGI POWYŻEJ TOLERANCJI", "WIDOCZNE USZKODZENIA MECHANICZNE / TRANSPORTOWE", "ODKŁOSY/OZNAKI PSUCIA – WYMAGA PRZEBRANIA NA MAGAZYNIE"])
elif st.session_state["status_jakosci"] == "CZERWONY":
    st.markdown('<div class="status-box" style="background-color: #e74c3c;">🔴 TOWAR ODRZUCONY - ZWROT</div>', unsafe_allow_html=True)
    komentarz_jakosc = st.text_input("Uzasadnienie zwrotu (wymagane):")

st.write("---")

# KROK 5: PODPIS DOSTAWCY I ZAMKNIĘCIE przez Pana Zbyszka
st.header("5. Podpis Dostawcy i Autoryzacja")

# Ramka na podpis dotykowy
st.markdown("✍️ **Kierowco / Dostawco: Podpisz się palcem w poniższej ramce:**")
canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 1)",
    stroke_width=3,
    stroke_color="#1F497D",
    background_color="#FFFFFF",
    height=150,
    width=400,
    drawing_mode="freedraw",
    key="canvas",
)

wybrany_magazynier = st.selectbox("Przyjmujący magazynier:", options=st.session_state["lista_magazynierow"] + ["➕ INNY MAGAZYNIER (DODAJ NA STAŁE)"])
if wybrany_magazynier == "➕ INNY MAGAZYNIER (DODAJ NA STAŁE)":
    nowy_m_imie = st.text_input("Wpisz Imię i Nazwisko nowego magazyniera:")
    if st.button("💾 ZAPISZ PRACOWNIKA NA LIŚCIE"):
        if nowy_m_imie:
            st.session_state["lista_magazynierow"].append(nowy_m_imie.strip())
            st.rerun()

if st.button("🔒 ZBIGNIEW ZATWIERDZA PRZYJĘCIE (GENERUJ PDF)"):
    if st.session_state["status_jakosci"] == "NIEWYBRANY":
        st.error("❌ Musisz wybrać ocenę jakościową!")
    elif wybrany_magazynier == "➕ INNY MAGAZYNIER (DODAJ NA STAŁE)":
        st.error("❌ Wybierz konkretnego pracownika z listy!")
    elif canvas_result.image_data is None:
        st.error("❌ Dostawca musi złożyć podpis w ramce!")
    else:
        # Konwersja rysunku z ramki na obrazek
        from PIL import Image as PILImage
        import numpy as np
        img_array = np.array(canvas_result.image_data)
        podpis_pil = PILImage.fromarray(img_array.astype('uint8'), 'RGBA')
        
        dane_d_koncowe = st.session_state["baza_dostawcow"][wybrany_id]
        losowy_nr_pz = f"PZ/{random.randint(10000,99999)}/{datetime.today().strftime('%Y')}"
        
        pdf_data = generuj_pdf_pz(
            losowy_nr_pz, automatyczna_data, wybrany_id, dane_d_koncowe, wybrany_towar,
            f"{rodzaj_opakowania} {szczegoly_opakowania} {nr_opakowania_sieciowego}", rodzaj_palety,
            ilosc_opakowan_laczna, ilosc_opakowan_pobranych, ilosc_palet_dostarczonych, ilosc_palet_pobranych,
            waga_netto_laczna, st.session_state["status_jakosci"], komentarz_jakosc, wybrany_magazynier, podpis_pil
        )
        
        st.success(f"🎉 ZBIGNIEW ZATWIERDZIŁ DOSTAWĘ! DOKUMENT {losowy_nr_pz} ZAPISANY W SYSTEMIE JANMAR.")
        st.balloons()
        
        st.download_button(
            label="📥 POBIERZ RAPORT PZ (PDF Z PODPISEM)",
            data=pdf_data,
            file_name=f"PZ_{wybrany_id}_{datetime.today().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )
