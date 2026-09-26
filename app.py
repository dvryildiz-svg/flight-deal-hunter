import os
import subprocess
import streamlit as st
from datetime import datetime
from bot import scan_multiple_dates

# Streamlit Cloud üzerinde Chromium tarayıcısının otomatik kurulmasını sağlar
try:
    import playwright
    subprocess.run(["playwright", "install", "chromium"], check=True)
except Exception as e:
    print(f"Playwright kurulum hatası: {e}")

st.set_page_config(page_title="Uçuş Avcısı Kontrol Paneli", page_icon="✈️", layout="wide")

st.title("✈️ Uçuş Avcısı Kontrol Paneli")

# Arayüz Formu
kalkis = st.text_input("Kalkış Havalimanı (Örn: IST)", value="IST")
varis = st.text_input("Varış Havalimanı (Örn: LHR)", value="LHR")

secenek_sayisi = st.number_input("Kaç farklı tarih seçeneği taramak istersiniz?", min_value=1, max_value=5, value=1)

tarih_listesi = []
for i in range(int(secenek_sayisi)):
    col1, col2 = st.columns(2)
    with col1:
        gidis = st.date_input(f"{i+1}. Seçenek Gidiş", key=f"gidis_{i}")
    with col2:
        donus = st.date_input(f"{i+1}. Seçenek Dönüş", key=f"donus_{i}")
    
    tarih_listesi.append((gidis.strftime("%Y/%m/%d"), donus.strftime("%Y/%m/%d")))

# Taramayı sadece butona basıldığında çalıştıran güvenli yapı
if st.button("🚀 Fırsatları Taramaya Başla"):
    with st.spinner("Google Flights taranıyor ve Telegram'a rapor iletiliyor, lütfen bekleyin..."):
        try:
            sonuc_raporu = scan_multiple_dates(kalkis, varis, tarih_listesi)
            st.success("Tarama başarıyla tamamlandı! Rapor Telegram'a iletildi.")
            
            # Ekranda raporu gösterme alanı
            st.markdown("### 🚨 GİDİŞ-DÖNÜŞ FIRSAT RAPORU 🚨")
            st.markdown(f"**Rota:** {kalkis} ↔️ {varis}")
            for item in sonuc_raporu:
                st.markdown(f"📅 {item}")
        except Exception as e:
            st.error(f"Tarama sırasında bir hata oluştu: {e}")
