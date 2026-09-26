import os
import time
import re
from datetime import datetime
from dotenv import load_dotenv
import requests
from playwright.sync_api import sync_playwright

load_dotenv()

TELEGRAM_BOT_TOKEN = "8929071599:AAGGNP7GDcO9x9LxpGvkjfe8xxcaBOPXbe4"
TELEGRAM_CHAT_ID = "8531946405"

def send_telegram_notification(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram bağlantı hatası: {e}")

def scan_multiple_dates(origin, destination, date_pairs):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Doğrudan Flights 'En ucuz' taraması başlatıldı: {origin} <-> {destination}")
    all_results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="tr-TR"
        )
        page = context.new_page()
        
        for gidis, donus in date_pairs:
            tarih_etiketi = f"{gidis} / {donus}"
            bot_url = f"https://www.google.com/travel/flights?q=uçuşlar%20{origin}%20-%20{destination}%20-%20{gidis}%20-%20{donus}&hl=tr"
            user_url = bot_url
            
            try:
                page.goto(bot_url, timeout=60000)
                
                # Google Flights "En ucuz" özet alanının yüklenmesini bekliyoruz
                try:
                    page.wait_for_selector("text=en düşük", timeout=30000)
                except:
                    pass
                
                time.sleep(5) # Verinin tamamen oturması için kısa bekleme
                
                page_text = page.locator("body").inner_text()
                
                # "en düşük:" ifadesinin hemen yanındaki fiyatı yakalıyoruz (örn: ₺8.761)
                lowest_price = None
                lines = page_text.split('\n')
                for i, line in enumerate(lines):
                    if "en düşük" in line.lower() or "en ucuz" in line.lower():
                        # Aynı satırda veya bir sonraki satırda fiyat arıyoruz
                        combined_chunk = line + " " + (lines[i+1] if i+1 < len(lines) else "")
                        matches = re.findall(r'₺\s*(\d{1,3}(?:\.\d{3})+|\d{4,6})', combined_chunk)
                        if not matches:
                            matches = re.findall(r'(\d{1,3}(?:\.\d{3})+|\d{4,6})', combined_chunk)
                        
                        if matches:
                            val_str = matches[0].replace('.', '')
                            if val_str.isdigit():
                                val = int(val_str)
                                if 4000 <= val <= 200000:
                                    lowest_price = f"₺{matches[0]}"
                                    break
                
                # Eğer özet satırından bulunamazsa sayfadaki ilk mantıklı uçuş fiyatını al
                if not lowest_price:
                    matches = re.findall(r'(\d{1,3}(?:\.\d{3})+|\d{4,6})', page_text)
                    valid_vals = []
                    for m in matches:
                        clean_num = m.replace('.', '')
                        if clean_num.isdigit():
                            val = int(clean_num)
                            if 4000 <= val <= 200000:
                                if val not in valid_vals:
                                    valid_vals.append(val)
                    if valid_vals:
                        valid_vals.sort()
                        lowest_price = f"₺{valid_vals[0]:,}".replace(',', '.')

                if lowest_price:
                    all_results.append(f"📅 **{tarih_etiketi}:** [✈️ {origin} ➡️ {destination} {lowest_price} (Bilet Al)]({user_url})")
                else:
                    all_results.append(f"📅 **{tarih_etiketi}:** [Fiyat Okunamadı - Tıklayıp Gör]({user_url})")
            except Exception as e:
                all_results.append(f"📅 **{tarih_etiketi}:** Tarama zaman aşımı/hata.")
        browser.close()
        
    final_message = f"🚨 **GİDİŞ-DÖNÜŞ FIRSAT RAPORU** 🚨\n\n**Rota:** {origin} <-> {destination}\n\n" + "\n".join(all_results) + f"\n\n⏱️ *Tarama Bitiş: {datetime.now().strftime('%H:%M')}*"
    send_telegram_notification(final_message)
    return final_message

def get_explore_deals(origin):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Keşfet taranıyor...")
    results = ["Keşfet modülü aktif."]
    final_message = "🌍 **ANLIK UCUZ ROTALAR** 🌍\n\n" + "\n".join(f"📍 {r}" for r in results)
    send_telegram_notification(final_message)
    return final_message

def get_airline_campaigns():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Kampanyalar taranıyor...")
    results = [
        "\n✈️ **[Türk Hava Yolları Kampanyaları](https://www.turkishairlines.com/tr-tr/kampanyalar/):**",
        "🔹 Güncel THY kampanyaları için tıklayın.",
        "\n✈️ **[AJet Kampanyaları](https://ajet.com/tr/ucak-bileti-kampanyalari/):**",
        "🔹 Güncel AJet kampanyaları için tıklayın."
    ]
    final_message = "📢 **GÜNCEL HAVAYOLU KAMPANYALARI** 📢\n" + "\n".join(results)
    send_telegram_notification(final_message)
    return final_message
