import time
from datetime import datetime
from playwright.sync_api import sync_playwright
import requests

TELEGRAM_TOKEN = "7547076949:AAF49zVpXG7R-H2q8r4_7q8r4_7q8r4_7q"
CHAT_ID = "SENIN_CHAT_ID"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Telegram mesajı gönderilemedi: {e}")

def scan_multiple_dates(origin, destination, date_pairs):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] İnteraktif Flights taraması başlatıldı: {origin} <-> {destination}")
    all_results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True, 
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="tr-TR"
        )
        page = context.new_page()

        for gidis, donus in date_pairs:
            tarih_etiketi = f"{gidis} / {donus}"
            
            # Doğrudan arama URL'si yerine arayüz simülasyonu için ana sayfa
            flight_url = f"https://www.google.com/travel/flights?hl=tr"
            
            try:
                page.goto(flight_url, timeout=60000)
                time.sleep(5)

                # Google'ın çerez/onay duvarı varsa geçmeye çalışalım
                try:
                    accept_button = page.query_selector("button[aria-label='Tümünü kabul et']")
                    if accept_button:
                        accept_button.click()
                        time.sleep(2)
                except:
                    pass

                # Kalkış ve varış alanlarını doldurmak için URL tabanlı filtreli arama URL'sini tekrar deneyelim ama bu kez sayfada bekleme süresini uzatalım
                search_url = f"https://www.google.com/travel/flights?q=Flights%20from%20{origin}%20to%20{destination}%20on%20{gidis}%20through%20{donus}&hl=tr"
                page.goto(search_url, timeout=60000)
                
                # Fiyatların DOM'a yüklenmesi için dinamik bekleme (Network Idle)
                try:
                    page.wait_for_load_state("networkidle", timeout=15000)
                except:
                    pass

                time.sleep(8) # Ekstra yüklenme payı

                bulunan_fiyat = None
                
                # Google Flights güncel fiyat kapsayıcıları
                selectors = [
                    'div[jsname="IqZcge"] span',
                    'span[jsname="pZAWMe"]',
                    'div.oVrid',
                    'span.unooUe'
                ]
                
                for selector in selectors:
                    try:
                        elements = page.query_selector_all(selector)
                        for el in elements:
                            text = el.inner_text().strip()
                            if ("₺" in text or "TL" in text) and len(text) < 15:
                                bulunan_fiyat = text
                                break
                        if bulunan_fiyat:
                            break
                    except:
                        continue

                if bulunan_fiyat:
                    rapor_metni = f"✈️ {origin} ➡️ {destination} | **{bulunan_fiyat}** ([Bilet Al]({search_url}))"
                    all_results.append(f"{tarih_etiketi}: {rapor_metni}")
                    send_telegram_message(f"🚨 **UÇUŞ FIRSATI BULUNDU!**\n\nRota: {origin} ➡️ {destination}\nTarih: {tarih_etiketi}\nFiyat: {bulunan_fiyat}\n\n[Google Flights'ta İncele]({search_url})")
                else:
                    all_results.append(f"{tarih_etiketi}: Fiyat etiketi yüklenemedi (Google bot koruması aktif).")

            except Exception as e:
                all_results.append(f"{tarih_etiketi}: Hata oluştu ({e})")

        browser.close()
    
    return all_results
