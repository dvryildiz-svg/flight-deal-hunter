import streamlit as st
from bot import scan_multiple_dates

st.set_page_config(page_title="Uçuş Avcısı Kontrol Paneli", page_icon="✈️", layout="wide")

st.title("✈️ Uçuş Avcısı Kontrol Paneli")
st.markdown("Hedef rotayı ve dilediğiniz sayıda gidiş-dönüş opsiyonunu belirleyerek botu çalıştırın.")

# Üst Menü Sekmeleri (Kampanya ve Fırsat Menüleri Geri Geldİ)
tab1, tab2, tab3 = st.tabs(["🎯 Gidiş-Dönüş Avcısı", "🌍 Ucuz Rotaları Keşfet", "📢 Havayolu Kampanyaları"])

with tab1:
    kalkis = st.text_input("Kalkış Havalimanı (Örn: IST)", value="IST", key="tab1_kalkis")
    varis = st.text_input("Varış Havalimanı (Örn: LHR)", value="LHR", key="tab1_varis")

    secenek_sayisi = st.number_input("Kaç farklı tarih seçeneği taramak istersiniz?", min_value=1, max_value=5, value=1, key="tab1_secenek")

    tarih_listesi = []
    for i in range(int(secenek_sayisi)):
        col1, col2 = st.columns(2)
        with col1:
            gidis = st.date_input(f"{i+1}. Seçenek Gidiş", key=f"gidis_{i}")
        with col2:
            donus = st.date_input(f"{i+1}. Seçenek Dönüş", key=f"donus_{i}")
        
        tarih_listesi.append((gidis.strftime("%Y/%m/%d"), donus.strftime("%Y/%m/%d")))

    if st.button("🚀 Fırsatları Taramaya Başla", key="btn_tab1"):
        with st.spinner("Uçuşlar taranıyor ve Telegram'a rapor iletiliyor, lütfen bekleyin..."):
            try:
                sonuc_raporu = scan_multiple_dates(kalkis, varis, tarih_listesi)
                st.success("Tarama başarıyla tamamlandı! Rapor Telegram'a iletildi.")
                
                st.markdown("### 🚨 GİDİŞ-DÖNÜŞ FIRSAT RAPORU 🚨")
                st.markdown(f"**Rota:** {kalkis} ➡️ {varis}")
                for item in sonuc_raporu:
                    st.markdown(f"📅 {item}")
            except Exception as e:
                st.error(f"Tarama sırasında bir hata oluştu: {e}")

with tab2:
    st.subheader("🌍 Ucuz Rotaları Keşfet")
    st.info("Popüler destinasyonlardaki en uygun fiyatlı dönemleri ve alternatif rotaları bu alandan hızlıca görüntüleyebilirsiniz.")
    st.markdown("* Aktif rota analizleri hazırlanıyor...")

with tab3:
    st.subheader("📢 Havayolu Kampanyaları")
    st.info("Türk Hava Yolları, Pegasus ve diğer anlaşmalı havayollarının güncel indirim ve promosyon kampanyaları listelenmektedir.")
    st.markdown("* Şu an aktif özel bir kampanya bulunmuyor.")
