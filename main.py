import os
import time
from datetime import datetime
from dotenv import load_dotenv
import requests
from playwright.sync_api import sync_playwright

load_dotenv()

TELEGRAM_BOT_TOKEN = "8929071599:AAGGNP7GDcO9x9LxpGvkjfe8xxcaBOPXbe4"
TELEGRAM_CHAT_ID = "8531946405"

def send_telegram_notification(message):
    """Fırsat yakalandığında Telegram üzerinden bildirim gönderir."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram bağlantı hatası: {e}")

def scan_multiple_dates(origin, destination, dates):
    """Belirtilen rotayı bir tarih listesi üzerinden sırayla tarar."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Çoklu tarama başlatıldı. Rota: {origin} -> {destination}")
    
    all_results = []
    
    with sync_playwright() as p:
        # Hata ayıklama için tarayıcıyı ekranda tutuyoruz
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        for date in dates:
            print(f"\n✈️ {date} tarihi için taranıyor...")
            # Değişkenlerle dinamik URL oluşturma
            url = f"https://www.google.com/travel/flights?q=Flights%20from%20{origin}%20to%20{destination}%20on%20{date}"
            
            try:
                page.goto(url, timeout=60000)
                
                # Ekranda '₺' sembolü belirene kadar bekle
                page.wait_for_selector("text=₺", timeout=20000)
                time.sleep(2) # Animasyon payı
                
                # Sayfadaki tüm düz metni al
                page_text = page.locator("body").inner_text()
                
                found_deals = []
                for line in page_text.split('\n'):
                    if '₺' in line:
                        clean_text = line.strip()
                        if len(clean_text) < 15 and clean_text not in found_deals:
                            found_deals.append(clean_text)
                
                if found_deals:
                    # Genelde ilk fiyat Google'ın önerdiği en düşük fiyattır
                    lowest_price = found_deals[0]
                    other_prices = ', '.join(found_deals[1:3])
                    all_results.append(f"📅 **{date}:** En düşük {lowest_price} *(Diğerleri: {other_prices})*")
                    print(f"Bulunan fiyatlar: {found_deals[:3]}")
                else:
                    all_results.append(f"📅 **{date}:** Fiyat okunamadı.")
                    
            except Exception as e:
                all_results.append(f"📅 **{date}:** Tarama zaman aşımı/hata.")
                print(f"Sayfa yüklenemedi: {e}")
        
        # Tüm tarihler bitince tarayıcıyı kapat
        browser.close()
        
    # Tüm sonuçları birleştirip tek mesaj olarak gönder
    final_message = (
        f"🚨 **ÇOKLU TARAMA FIRSAT RAPORU** 🚨\n\n"
        f"**Rota:** {origin} -> {destination}\n\n"
        + "\n".join(all_results) +
        f"\n\n⏱️ *Tarama Bitiş: {datetime.now().strftime('%d.%m.%Y %H:%M')}*"
    )
    
    send_telegram_notification(final_message)
    print("\n✅ Toplu rapor Telegram'a başarıyla iletildi!")

if __name__ == "__main__":
    # Test için değişkenlerimiz: Kalkış, Varış ve 5 opsiyonlu tarih
    kalkis_noktasi = "IST"
    varis_noktasi = "LHR"
    tarih_opsiyonlari = [
        "2026-10-15", 
        "2026-10-16", 
        "2026-10-17", 
        "2026-10-18", 
        "2026-10-19"
    ]
    
    scan_multiple_dates(kalkis_noktasi, varis_noktasi, tarih_opsiyonlari)
