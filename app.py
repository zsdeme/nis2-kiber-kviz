import streamlit as st
import json
import random
import plotly.graph_objects as go

st.set_page_config(page_title="NIS2 Kiberbiztonsági Kvíz", page_icon="🛡️", layout="centered",)


@st.cache_data
def load_questions():
    with open('questions.json', 'r', encoding='utf-8') as f:
        return json.load(f)


all_questions = load_questions()

# Állapotváltozók inicializálása
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False
    st.session_state.vege = False
    st.session_state.aktualis_index = 0
    st.session_state.osszes_pont = 0
    st.session_state.kategoriak = {}
    st.session_state.valaszolt = False
    st.session_state.helyes_volt = None
    st.session_state.session_questions = []
    st.session_state.max_pont = 0

st.title("🛡️ NIS2 Kiberbiztonsági Kvíz", anchor=False)

# ---- 1. Kezdőképernyő és nehézségek kiválasztása ----
if not st.session_state.quiz_started:
    st.write("Üdvözlünk a NIS2-alapú kiberbiztonsági felmérőben!")
    st.write("Kérlek, válaszd ki a teszt hosszát a kezdéshez:")

    mode = st.radio(
        "Nehézségi szint:",
        [
            "🟢 Normál Mód (20 kérdés - Gyors, napi mikrotanuláshoz)",
            "🔴 Hardcore Mód (100 kérdés - Teljes NIS2 audit)"
        ]
    )

    if st.button("🚀 Kvíz indítása"):
        # Kérdések kategóriánkénti csoportosítása (Rétegzett mintavétel)
        kategoriak_dict = {}
        for q in all_questions:
            kat = q['kategoria']
            if kat not in kategoriak_dict:
                kategoriak_dict[kat] = []
            kategoriak_dict[kat].append(q)

        # Kérdések kiválasztása a mód alapján (5 vagy 25 kategóriánként)
        kerdes_per_kategoria = 5 if "Normál" in mode else 25

        kivalasztott_kerdesek = []
        for kat, kerdesek in kategoriak_dict.items():
            kivalasztott_kerdesek.extend(random.sample(kerdesek, min(kerdes_per_kategoria, len(kerdesek))))

        # Összekeverjük a végső listát, hogy ne egymás után jöjjenek az azonos kategóriájú kérdések
        random.shuffle(kivalasztott_kerdesek)

        # Beállítjuk a memóriát a kvízhez
        st.session_state.session_questions = kivalasztott_kerdesek
        st.session_state.max_pont = sum(q['suly'] for q in kivalasztott_kerdesek)
        st.session_state.quiz_started = True
        st.rerun()

# ---- 2. Kvíz játékmenet ----
elif not st.session_state.vege:
    progress = st.session_state.aktualis_index / len(st.session_state.session_questions)
    st.progress(progress)
    st.write(f"Kérdés: {st.session_state.aktualis_index + 1} / {len(st.session_state.session_questions)}")

    q = st.session_state.session_questions[st.session_state.aktualis_index]

    st.subheader(q['kategoria'], anchor=False)
    st.markdown(f"**{q['kerdes']}** *(Érték: {q['suly']} pont)*")

    valasztott = st.radio(
        "Válaszd ki a helyes megoldást:",
        q['valaszok'],
        index=None,
        disabled=st.session_state.valaszolt
    )

    if not st.session_state.valaszolt:
        if st.button("Válasz beküldése"):
            if valasztott is None:
                st.warning("Kérlek válassz egy opciót!")
            else:
                st.session_state.valaszolt = True
                st.session_state.felhasznalo_valasza = valasztott

                # --- Pontszámítás ---
                if q['kategoria'] not in st.session_state.kategoriak:
                    st.session_state.kategoriak[q['kategoria']] = {'elert': 0, 'max': 0}

                st.session_state.kategoriak[q['kategoria']]['max'] += q['suly']

                if valasztott == q['valaszok'][q['helyes_valasz_index']]:
                    st.session_state.helyes_volt = True
                    st.session_state.osszes_pont += q['suly']
                    st.session_state.kategoriak[q['kategoria']]['elert'] += q['suly']
                else:
                    st.session_state.helyes_volt = False

                st.rerun()

    else:
        if st.session_state.helyes_volt:
            st.success(f"✅ Helyes! (+{q['suly']} pont)")
        else:
            st.error("❌ Helytelen válasz.")

        st.info(f"💡 **Tanulság:** {q['magyarazat']}")

        if st.button("Következő ➡️"):
            st.session_state.valaszolt = False
            st.session_state.helyes_volt = None
            st.session_state.aktualis_index += 1

            if st.session_state.aktualis_index >= len(st.session_state.session_questions):
                st.session_state.vege = True
            st.rerun()

# ---- 3. Értékelés és badgek ----
else:
    st.balloons()
    st.header("🏆 Kvíz sikeresen befejezve!", anchor=False)

    szazalek = (st.session_state.osszes_pont / st.session_state.max_pont) * 100

    if szazalek < 41:
        rang, ikon, uzenet = "Kiber-Újonc", "⚠️", "Kritikus kockázat! Javasoljuk az alapok átismétlését."
    elif szazalek < 76:
        rang, ikon, uzenet = "Tudatos Felhasználó", "🛡️", "Jó alapok, de a trükkösebb támadások még veszélyt jelenthetnek."
    elif szazalek < 96:
        rang, ikon, uzenet = "Kiber-Védelmező", "🦅", "Kiváló kiberhigiénia, biztonságosan mozogsz a digitális térben!"
    else:
        rang, ikon, uzenet = "Humán Tűzfal (NIS2 Bajnok)", "🏆", "Tökéletes eredmény! Rajtad nem fognak ki a hackerek!"

    st.subheader(f"Elért Rangod: {ikon} {rang}", anchor=False)
    st.write(uzenet)
    st.write(f"**Végső pontszám:** {st.session_state.osszes_pont} / {st.session_state.max_pont} ({szazalek:.1f}%)")

    st.divider()
    st.subheader("📊 Kategóriánkénti Kockázati Index", anchor=False)

    # --- Radardiagram előkészítése ---
    kategoriak_nevei = list(st.session_state.kategoriak.keys())
    kategoriak_ertekek = [(st.session_state.kategoriak[k]['elert'] / st.session_state.kategoriak[k]['max']) * 100 for k
                          in kategoriak_nevei]

    # Kör bezárása a diagramhoz
    radar_nevek = kategoriak_nevei.copy()
    radar_ertekek = kategoriak_ertekek.copy()
    if len(radar_nevek) > 2:
        radar_nevek.append(radar_nevek[0])
        radar_ertekek.append(radar_ertekek[0])

    # Radardiagram megrajzolása
    fig = go.Figure(data=go.Scatterpolar(
        r=radar_ertekek,
        theta=radar_nevek,
        fill='toself',
        line_color='#4169E1',
        name='Elért %'
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        margin=dict(l=40, r=40, t=20, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- Százalékos sávok ---
    st.divider()
    st.subheader("📈 Részletes eredmények", anchor=False)

    for kat, pontok in st.session_state.kategoriak.items():
        kat_szaz = (pontok['elert'] / pontok['max']) * 100
        st.write(f"{kat}: **{kat_szaz:.0f}%**")
        st.progress(kat_szaz / 100)

    if st.button("🔄 Vissza a Főmenübe"):
        st.session_state.clear()
        st.rerun()