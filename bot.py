import time
from datetime import datetime
from playwright.sync_api import sync_playwright
import requests
import os

# Telegram Bilgileri (Güvenli olması için buraya doğrudan yazabilir veya sabit tutabilirsin)
TELEGRAM_TOKEN = "7547076949:AAF49zVpXG7R-H2q8r4_7q8r4_7q8r4_7q"  # Kendi token'ın
CHAT_ID = "SENIN_CHAT_ID"  # Kendi Chat ID'n

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
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Doğrudan Flights 'En ucuz' taraması başlatıldı: {origin} <-> {destination}")
    all_results = []

    # Bulut sunucularda çökmemesi için headless=True ve ek sandbox argümanları eklendi
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
            bot_url = f"https://www.google.com/travel/flights?q=uçuşlar%20{origin}%20-{destination}%20%20{gidis}%20-%20{donus}&hl=tr"
            
            try:
                page.goto(bot_url, timeout=60000)
                
                try:
                    page.wait_for_selector("text=en düşük", timeout=30000)
                except:
                    pass

                time.sleep(5) # Sayfanın tamamen yüklenmesi için kısa bir bekleme

                # CSS Seçici ile fiyat etiketini yakalama
                price_elements = page.query_selector_all('div[jsname="IqZcge"] span, span[jsname="pZAWMe"]')
                
                bulunan_fiyat = None
                for el in price_elements:
                    text = el.inner_text().strip()
                    if "₺" in text or "TL" in text:
                        bulunan_fiyat = text
                        break

                if bulunan_fiyat:
                    rapor_metni = f"✈️ {origin} ➡️ {destination} {bulunan_fiyat} ([Bilet Al]({bot_url}))"
                    all_results.append(f"{tarih_etiketi}: {rapor_metni}")
                    
                    # Telegram bildirimi gönder
                    send_telegram_message(f"🚨 **UÇUŞ FIRSATI BULUNDU!**\n\nRota: {origin} ➡️ {destination}\nTarih: {tarih_etiketi}\nFiyat: {bulunan_fiyat}\n\n[Google Flights'ta İncele]({bot_url})")
                else:
                    all_results.append(f"{tarih_etiketi}: Fiyat etiketi otomatik algılanamadı.")

            except Exception as e:
                all_results.append(f"{tarih_etiketi}: Hata oluştu ({e})")

        browser.close()
    
    return all_results
