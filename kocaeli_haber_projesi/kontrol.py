"""
kontrol.py
"""
import os
from dotenv import load_dotenv
load_dotenv()

def kontrol_et():
    hatalar = []
    print("=" * 55)
    print("  Sistem Kontrolü")
    print("=" * 55)

    if not os.path.exists(".env"):
        hatalar.append(".env dosyası bulunamadı!")
    else:
        print("✅ .env dosyası mevcut")

    mk = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if mk and "BURAYA" not in mk:
        print(f"✅ GOOGLE_MAPS_API_KEY ({mk[:10]}...)")
    else:
        hatalar.append("GOOGLE_MAPS_API_KEY ayarlanmamış!")

    gk = os.getenv("GOOGLE_GEOCODING_API_KEY", "")
    if gk and "BURAYA" not in gk:
        print(f"✅ GOOGLE_GEOCODING_API_KEY ({gk[:10]}...)")
    else:
        hatalar.append("GOOGLE_GEOCODING_API_KEY ayarlanmamış!")

    try:
        from database import db
        db.command("ping")
        print("✅ MongoDB bağlantısı başarılı")
    except Exception as e:
        hatalar.append(f"MongoDB hatası: {e}")

    for mod, isim in {"flask":"Flask","pymongo":"PyMongo","requests":"Requests","bs4":"BeautifulSoup4","dotenv":"python-dotenv"}.items():
        try:
            __import__(mod)
            print(f"✅ {isim}")
        except ImportError:
            hatalar.append(f"{isim} yüklü değil!")

    try:
        import sentence_transformers
        print("✅ sentence-transformers")
    except ImportError:
        print("⚠️  sentence-transformers yüklü değil (embedding için gerekli)")

    print("\n" + "=" * 55)
    if hatalar:
        for h in hatalar:
            print(f"❌ {h}")
    else:
        print("✅ Tüm kontroller başarılı!")
    print("=" * 55)

if __name__ == "__main__":
    kontrol_et()






