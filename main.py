import os
import time
from datetime import datetime
from dotenv import load_dotenv
import requests
from playwright.sync_api import sync_playwright

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_notification(message):
    """Fırsat yakalandığında Telegram üzerinden bildirim gönderir."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bilgileri eksik, mesaj gönderilemedi.")
        print(f"Mesaj içeriği: {message}")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Telegram mesajı gönderilemedi: {response.text}")
    except Exception as e:
        print(f"Bağlantı hatası: {e}")

def check_flights_with_browser():
    """Playwright ile uçuş sitelerini tarayan bot fonksiyonu."""
    print(f"[{datetime.now()}] Tarayıcı botu iş başucunda, uçuşlar taranıyor...")
    
    with sync_playwright() as p:
        # Tarayıcıyı açıyoruz (headless=False yaparsan tarayıcının ekranda açıldığını görürsün)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Örnek olarak Google Flights üzerinden İstanbul - Londra araması simüle edelim
            url = "https://www.google.com/travel/flights?q=Flights%20from%20IST%20to%20LHR%20on%202026-10-15"
            print(f"Hedef sayfaya gidiliyor: {url}")
            page.goto(url, timeout=60000)
            
            # Sayfanın yüklenmesi için biraz bekleyelim
            time.sleep(5)
            
            # Sayfadaki fiyat elementlerini yakalamaya çalışalım 
            # (Google Flights dinamik yapıda olduğu için seçiciler değişebilir, temel bir mantık kuruyoruz)
            prices = page.locator('div[role="main"] span').all_text_contents()
            
            found_deals = []
            for text in prices:
                # Metin içerisinde fiyat belirten TL veya rakamları ayıklama mantığı
                if "TL" in text or "₺" in text:
                    found_deals.append(text)
            
            print(f"Bulunan fiyat metinleri: {found_deals[:5]}")
            
            # Simüle edilmiş bir fırsat bildirimi kurgulayalım
            # Gerçek senaryoda buraya çektiğimiz fiyatları filtreleme mantığı ekleyeceğiz.
            sample_deal_msg = (
                f"🚨 **TARAYICI BOTU FIRSAT RAPORU** 🚨\n\n"
                f"✈️ **Rota:** İstanbul -> Londra (LHR)\n"
                f"🔍 Bot başarıyla tarama yaptı ve sayfadaki verileri okudu!\n"
                f"📅 **Zaman:** {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            )
            
            send_telegram_notification(sample_deal_msg)
            
        except Exception as e:
            print(f"Tarama sırasında hata oluştu: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    check_flights_with_browser()
