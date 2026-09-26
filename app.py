import os
import subprocess

# Streamlit Cloud üzerinde Chromium tarayıcısının otomatik kurulmasını sağlar
try:
    import playwright
    subprocess.run(["playwright", "install", "chromium"], check=True)
except Exception as e:
    print(f"Playwright kurulum hatası: {e}")

import streamlit as st
from bot import scan_multiple_dates, get_explore_deals, get_airline_campaigns

st.set_page_config(page_title="Uçuş Avcısı", page_icon="✈️", layout="centered")

st.title("🛫 Uçuş Avcısı Kontrol Paneli")

# 3 farklı işlem için sekmeler oluşturuyoruz
tab1, tab2, tab3 = st.tabs(["🎯 Gidiş-Dönüş Avcısı", "🌍 Ucuz Rotaları Keşfet", "📢 Havayolu Kampanyaları"])

with tab1:
    st.markdown("Hedef rotayı ve dilediğiniz sayıda gidiş-dönüş opsiyonunu belirleyerek botu çalıştırın.")
    col1, col2 = st.columns(2)
    with col1:
        kalkis = st.text_input("Kalkış Havalimanı (Örn: IST)", value="IST").upper()
    with col2:
        varis = st.text_input("Varış Havalimanı (Örn: LHR)", value="LHR").upper()
        
    secenek_sayisi = st.number_input("Kaç farklı tarih seçeneği taramak istersiniz?", min_value=1, max_value=10, value=1, step=1)
    
    tarih_listesi = []
    for i in range(1, int(secenek_sayisi) + 1):
        c1, c2 = st.columns(2)
        with c1:
            gidis = st.date_input(f"{i}. Seçenek Gidiş", key=f"g_{i}")
        with c2:
            donus = st.date_input(f"{i}. Seçenek Dönüş", key=f"d_{i}")
        tarih_listesi.append((gidis.strftime("%Y-%m-%d"), donus.strftime("%Y-%m-%d")))

    if st.button("🚀 Fırsatları Taramaya Başla", use_container_width=True):
        with st.spinner(f"{secenek_sayisi} farklı gidiş-dönüş kombinasyonu taranıyor..."):
            sonuc_raporu = scan_multiple_dates(kalkis, varis, tarih_listesi)
        st.success("✅ Tarama başarıyla tamamlandı! Rapor Telegram'a iletildi.")
        st.info(sonuc_raporu)

with tab2:
    st.markdown("Belirlediğiniz kalkış noktasından gidebileceğiniz **en ucuz anlık rotaları** Google Flights üzerinden tarayın.")
    kesfet_kalkis = st.text_input("Nereden Çıkış Yapılacak? (Örn: IST)", value="IST", key="kesfet").upper()
    
    if st.button("🔥 Ucuz Rotaları Keşfet", use_container_width=True):
        with st.spinner(f"{kesfet_kalkis} çıkışlı en ucuz rotalar aranıyor..."):
            kesfet_raporu = get_explore_deals(kesfet_kalkis)
        st.success("✅ Keşfet taraması tamamlandı! Rapor Telegram'a iletildi.")
        st.info(kesfet_raporu)

with tab3:
    st.markdown("Türk Hava Yolları ve AJet'in resmi web sitelerindeki **güncel promosyon ve indirim duyurularını** tek tıkla çekin.")
    
    if st.button("📢 Kampanyaları Tara (THY & AJet)", use_container_width=True):
        with st.spinner("Havayolu firmalarının resmi siteleri taranıyor..."):
            kampanya_raporu = get_airline_campaigns()
        st.success("✅ Kampanya taraması tamamlandı! Rapor Telegram'a iletildi.")
        st.info(kampanya_raporu)
