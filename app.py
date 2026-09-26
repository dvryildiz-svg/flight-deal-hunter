import streamlit as st
from bot import scan_multiple_dates

st.set_page_config(page_title="Uçuş Avcısı Kontrol Paneli", page_icon="✈️", layout="wide")

st.title("✈️ Uçuş Avcısı Kontrol Paneli")
st.markdown("Hedef rotayı ve dilediğiniz tarih opsiyonlarını belirleyerek canlı taramayı hemen başlatın.")

# Yan yana düzen için kolonlar
col_form, col_rapor = st.columns([1, 1])

with col_form:
    st.subheader("⚙️ Arama Parametreleri")
    kalkis = st.text_input("Kalkış Havalimanı (Örn: IST)", value="IST")
    varis = st.text_input("Varış Havalimanı (Örn: LHR)", value="LHR")

    secenek_sayisi = st.number_input("Kaç farklı tarih seçeneği taramak istersiniz?", min_value=1, max_value=5, value=1)

    tarih_listesi = []
    for i in range(int(secenek_sayisi)):
        c1, c2 = st.columns(2)
        with c1:
            gidis = st.date_input(f"{i+1}. Gidiş Tarihi", key=f"gidis_{i}")
        with c2:
            donus = st.date_input(f"{i+1}. Dönüş Tarihi", key=f"donus_{i}")
        
        tarih_listesi.append((gidis.strftime("%Y/%m/%d"), donus.strftime("%Y/%m/%d")))

    calistir = st.button("🚀 Fırsatları Taramaya Başla", type="primary")

with col_rapor:
    st.subheader("📊 Fırsat ve Tarama Raporu")
    
    if calistir:
        with st.spinner("Uçuşlar taranıyor ve Telegram'a rapor iletiliyor..."):
            try:
                sonuc_raporu = scan_multiple_dates(kalkis, varis, tarih_listesi)
                st.success("Tarama başarıyla tamamlandı! Rapor Telegram'a iletildi.")
                
                st.markdown(f"**Rota:** {kalkis} ➡️ {varis}")
                for item in sonuc_raporu:
                    st.info(item)
            except Exception as e:
                st.error(f"Hata oluştu: {e}")
    else:
        st.info("Sol taraftan kriterleri belirleyip 'Fırsatları Taramaya Başla' butonuna basın. Sonuçlar burada görünecektir.")

# Alt Bilgi / Kampanya Alanı
st.markdown("---")
st.markdown("📢 **Aktif Kampanyalar & Bilgilendirme:** Sistem şu an API tabanlı canlı modda çalışmaktadır. Telegram bildirimleriniz anlık olarak iletilir.")
