import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# .env dosyasındaki gizli bilgileri yükle (Lokalde test ederken kullanırsın)
load_dotenv()

# --- YAPILANDIRMA (CONFIG) ---
API_KEY = os.getenv("API_KEY") 
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Çıkış Havalimanı (İstanbul)
FLY_FROM = "IST,SAW"

# Hedef Bölgeler / Ülkeler (Avrupa ve Amerika ana hatları)
TARGET_LOCATIONS = ["GB", "FR", "DE", "NL", "US", "ES"] 

def send_telegram_notification(message):
    """Fırsat yakalandığında Telegram üzerinden bildirim gönderir."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bilgileri eksik, mesaj gönderilemedi.")
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

def check_flight_deals():
    """Kiwi API üzerinden belirli rotalardaki fiyatları tarar ve eşikleri kontrol eder."""
    print(f"[{datetime.now()}] Uçuş fiyatları taranıyor...")
    
    if not API_KEY:
        print("API_KEY bulunamadı!")
        return

    date_from = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")
    date_to = (datetime.now() + timedelta(days=90)).strftime("%d/%m/%Y")
    
    url = "https://api.tequila.kiwi.com/v2/search"
    headers = {"apikey": API_KEY}
    
    for country in TARGET_LOCATIONS:
        params = {
            "fly_from": FLY_FROM,
            "fly_to": f"country:{country}",
            "date_from": date_from,
            "date_to": date_to,
            "curr": "TRY",
            "limit": 5,
            "sort": "price"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                flights = data.get("data", [])
                
                for flight in flights:
                    price = flight.get("price")
                    destination = flight.get("cityTo")
                    country_to = flight.get("countryTo", {}).get("name")
                    departure_date = datetime.fromtimestamp(flight.get("dTime")).strftime('%d.%m.%Y')
                    airline = ", ".join(flight.get("airlines", []))
                    booking_link = flight.get("deep_link")
                    
                    is_deal = False
                    if country in ["US"] and price < 15000:
                        is_deal = True
                    elif country in ["GB", "FR", "DE", "NL", "ES"] and price < 5000:
                        is_deal = True
                        
                    if is_deal:
                        msg = (
                            f"🚨 **FLAŞ UÇUŞ FIRSATI!** 🚨\n\n"
                            f"✈️ **Rota:** İstanbul -> {destination} ({country_to})\n"
                            f"💰 **Fiyat:** {price} TL\n"
                            f"📅 **Tarih:** {departure_date}\n"
                            f"🏢 **Havayolu:** {airline}\n\n"
                            f"[Bileti İncele & Al]({booking_link})"
                        )
                        send_telegram_notification(msg)
            else:
                print(f"API Hatası ({country}): {response.status_code}")
        except Exception as e:
            print(f"İstek sırasında hata oluştu: {e}")

if __name__ == "__main__":
    check_flight_deals()
