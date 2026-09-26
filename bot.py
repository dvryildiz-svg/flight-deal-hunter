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
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Stealth tarama başlatıldı: {origin} <-> {destination}")
    all_results = []

    with sync_playwright() as p:
        # Bot korumalarını atlatmak için gelişmiş tarayıcı argümanları
        browser = p.chromium.launch(
            headless=True, 
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled", # Bot olduğunun anlaşılmasını engeller
                "--disable-infobars",
                "--window-size=1920,1080"
            ]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="tr-TR",
            viewport={"width": 1920, "height": 1080}
        )
        
        # navigator.webdriver özelliğini gizleyerek bot korumasını kandır
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = context.new_page()

        for gidis, donus in date_pairs:
            tarih_etiketi = f"{gidis} / {donus}"
            search_url = f"https://www.google.com/travel/flights?q=Flights%20from%20{origin}%20to%20{destination}%20on%20{gidis}%20through%20{donus}&hl=tr"
            
            try:
                page.goto(search_url, timeout=60000)
                
                # Sayfanın insan hareketlerini taklit ederek yüklenmesini bekle
                time.sleep(10)
                
                # Sayfada aşağı yukarı hafif hareketler simüle et
                page.mouse.wheel(0, 300)
                time.sleep(3)

                bulunan_fiyat = None
                
                # Fiyat elementlerini yakalamak için güncel seçiciler
                selectors = [
                    'div[jsname="IqZcge"] span',
                    'span[jsname="pZAWMe"]',
                    'div.oVrid span',
                    'span.fsw-text',
                    'div.YMlIz'
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
                    all_results.append(f"{tarih_etiketi}: Fiyat korumaya takıldı. Alternatif rota denenebilir.")

            except Exception as e:
                all_results.append(f"{tarih_etiketi}: Hata oluştu ({e})")

        browser.close()
    
    return all_results
