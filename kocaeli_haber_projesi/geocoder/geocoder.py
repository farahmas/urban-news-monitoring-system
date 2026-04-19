"""
geocoder.py

"""

import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from database import haberler_col, geocache_col

GOOGLE_API_KEY = os.getenv("GOOGLE_GEOCODING_API_KEY", "")

ILCE_KOORDINATLARI = {
    "İzmit":      {"enlem": 40.7654, "boylam": 29.9408},
    "Gebze":      {"enlem": 40.8027, "boylam": 29.4305},
    "Darıca":     {"enlem": 40.7669, "boylam": 29.3736},
    "Gölcük":     {"enlem": 40.6531, "boylam": 29.8275},
    "Körfez":     {"enlem": 40.7731, "boylam": 29.7981},
    "Derince":    {"enlem": 40.7375, "boylam": 29.8131},
    "Çayırova":   {"enlem": 40.8219, "boylam": 29.3731},
    "Kartepe":    {"enlem": 40.6833, "boylam": 29.9667},
    "Başiskele":  {"enlem": 40.7167, "boylam": 29.8833},
    "Karamürsel": {"enlem": 40.6833, "boylam": 29.6167},
    "Kandıra":    {"enlem": 41.0667, "boylam": 30.1500},
    "Dilovası":   {"enlem": 40.7833, "boylam": 29.5167},
}


def normalize_konum(konum_metni):
    if not konum_metni:
        return ""

    metin = str(konum_metni).strip()

    degisimler = {
        "Mah.": "Mahallesi",
        "Mah ": "Mahallesi ",
        "Cad.": "Caddesi",
        "Cad ": "Caddesi ",
        "Sok.": "Sokak",
        "Sok ": "Sokak ",
        "Blv.": "Bulvarı",
        "Blv ": "Bulvarı ",
    }

    for eski, yeni in degisimler.items():
        metin = metin.replace(eski, yeni)

    metin = " ".join(metin.split())
    return metin


def cache_kontrol(konum_metni):
    norm = normalize_konum(konum_metni)
    kayit = geocache_col.find_one({"konum_metni": norm})
    if kayit:
        return kayit.get("enlem"), kayit.get("boylam")
    return None, None


def cache_kaydet(konum_metni, enlem, boylam):
    norm = normalize_konum(konum_metni)
    geocache_col.update_one(
        {"konum_metni": norm},
        {"$set": {"konum_metni": norm, "enlem": enlem, "boylam": boylam}},
        upsert=True
    )


def sadece_ilce_mi(konum_metni):
    norm = normalize_konum(konum_metni).lower()
    for ilce in ILCE_KOORDINATLARI.keys():
        ilce_k = ilce.lower()
        if norm in {
            ilce_k,
            f"{ilce_k}, kocaeli",
            f"{ilce_k}, kocaeli, türkiye"
        }:
            return True
    return False


def ilce_koordinati_bul(konum_metni):
    konum_kucuk = normalize_konum(konum_metni).lower().replace("İ", "i").replace("I", "ı")
    for ilce, koordinat in ILCE_KOORDINATLARI.items():
        ilce_kucuk = ilce.lower().replace("İ", "i").replace("I", "ı")
        if ilce_kucuk in konum_kucuk:
            return koordinat["enlem"], koordinat["boylam"]
    return None, None


def sonuc_kocaeli_mi(sonuc):
    try:
        components = sonuc.get("address_components", [])
        tum_bilesenler = " ".join(
            c.get("long_name", "") + " " + c.get("short_name", "")
            for c in components
        ).lower()

        if "kocaeli" in tum_bilesenler:
            return True

        geometry = sonuc.get("geometry", {}).get("location", {})
        enlem = geometry.get("lat")
        boylam = geometry.get("lng")

        if enlem is None or boylam is None:
            return False

        return 40.5 <= enlem <= 41.2 and 29.0 <= boylam <= 30.5
    except Exception:
        return False


def google_geocode(konum_metni):
    if not GOOGLE_API_KEY:
        print("  ⚠️  Google API key bulunamadı! .env dosyasını kontrol edin.")
        return None, None

    norm = normalize_konum(konum_metni)

    adres = norm
    if "kocaeli" not in norm.lower():
        adres = f"{norm}, Kocaeli, Türkiye"

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": adres,
        "key": GOOGLE_API_KEY,
        "language": "tr",
        "region": "tr",
        "bounds": "40.5000,29.0000|41.2000,30.5000"
    }

    try:
        cevap = requests.get(url, params=params, timeout=10)
        cevap.raise_for_status()
        veri = cevap.json()

        if veri.get("status") == "OK" and veri.get("results"):
            for sonuc in veri["results"]:
                if not sonuc_kocaeli_mi(sonuc):
                    continue

                lokasyon = sonuc["geometry"]["location"]
                enlem = lokasyon["lat"]
                boylam = lokasyon["lng"]

                if 40.5 <= enlem <= 41.2 and 29.0 <= boylam <= 30.5:
                    return enlem, boylam

            print(f"  ⚠️  Uygun Kocaeli sonucu bulunamadı: {norm[:60]}")
            return None, None
        else:
            print(f"  ⚠️  Google API status: {veri.get('status')}")

    except Exception as e:
        print(f"  ⚠️  Google Geocoding hatası ({norm[:40]}): {e}")

    return None, None


def koordinat_bul(konum_metni):
    

    if not konum_metni or konum_metni in ("Belirtilmemiş", "Kocaeli", ""):
        return None, None

    norm = normalize_konum(konum_metni)

    enlem, boylam = cache_kontrol(norm)
    if enlem is not None and boylam is not None:
        return enlem, boylam

    if sadece_ilce_mi(norm):
        enlem, boylam = ilce_koordinati_bul(norm)
        if enlem is not None and boylam is not None:
            cache_kaydet(norm, enlem, boylam)
            return enlem, boylam

    enlem, boylam = google_geocode(norm)
    if enlem is not None and boylam is not None:
        cache_kaydet(norm, enlem, boylam)
        return enlem, boylam

    enlem, boylam = ilce_koordinati_bul(norm)
    if enlem is not None and boylam is not None:
        cache_kaydet(norm, enlem, boylam)
        return enlem, boylam

    return None, None


def tum_haberleri_geocode_et():
    koordinatsiz = list(haberler_col.find({
        "enlem": None,
        "konum_metni": {"$nin": ["Belirtilmemiş", "Kocaeli", None, ""]},
        "gecersiz_tur": {"$ne": True},
        "kocaeli_disi": {"$ne": True}
    }))

    toplam = len(koordinatsiz)
    if toplam == 0:
        print("🗺️  Geocoding: İşlenecek haber yok.")
        return

    print(f"\n🗺️  Google Geocoding başlıyor... ({toplam} haber işlenecek)")
    basarili = 0
    basarisiz = 0

    for haber in koordinatsiz:
        konum = haber.get("konum_metni", "")
        enlem, boylam = koordinat_bul(konum)

        if enlem is not None and boylam is not None:
            haberler_col.update_one(
                {"_id": haber["_id"]},
                {
                    "$set": {
                        "enlem": enlem,
                        "boylam": boylam,
                        "geocode_durumu": "basarili"
                    },
                    "$unset": {
                        "geocode_hata": ""
                    }
                }
            )
            basarili += 1
            print(f"  ✅ {konum[:60]} → {enlem:.4f}, {boylam:.4f}")
        else:
            haberler_col.update_one(
                {"_id": haber["_id"]},
                {
                    "$set": {
                        "geocode_durumu": "basarisiz",
                        "geocode_hata": konum
                    }
                }
            )
            basarisiz += 1
            print(f"  ❌ Koordinat bulunamadı: {konum[:60]}")

    print(f"\n  📊 Başarılı: {basarili} | Başarısız: {basarisiz}")


if __name__ == "__main__":
    tum_haberleri_geocode_et()

