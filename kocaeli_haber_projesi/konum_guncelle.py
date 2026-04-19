"""
konum_guncelle.py

"""

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import haberler_col
from geocoder.geocoder import tum_haberleri_geocode_et
from scrapers.base_scraper import BaseScraper


def ilce_alani_guncelle():
    scraper = BaseScraper("temp", "temp")
    haberler = list(haberler_col.find({
        "$or": [{"ilce": {"$exists": False}}, {"ilce": None}]
    }))
    print(f"\n📍 Ilce alani guncellenecek: {len(haberler)} haber")
    g = 0
    for h in haberler:
        konum = h.get("konum_metni", "")
        baslik = h.get("haber_basligi", "")
        icerik = h.get("haber_icerigi", "")
        ilce = scraper.ilce_bul(konum) or scraper.ilce_bul(baslik + " " + icerik)
        if ilce:
            haberler_col.update_one({"_id": h["_id"]}, {"$set": {"ilce": ilce}})
            g += 1
    print(f"  ✅ {g} habere ilce eklendi.")


def siniflandirma_duzelt():
    scraper = BaseScraper("temp", "temp")
    haberler = list(haberler_col.find({
        "$or": [{"haber_turu": "Diğer"}, {"haber_turu": None}, {"haber_turu": {"$exists": False}}]
    }))
    print(f"\n🏷️  Siniflandirma duzeltilecek: {len(haberler)} haber")
    d, s = 0, 0
    for h in haberler:
        yeni = scraper.haber_turunu_bul(h.get("haber_basligi",""), h.get("haber_icerigi",""))
        if yeni:
            haberler_col.update_one({"_id": h["_id"]}, {"$set": {"haber_turu": yeni}})
            d += 1
        else:
            haberler_col.delete_one({"_id": h["_id"]})
            s += 1
    print(f"  ✅ Duzeltilen: {d} | Silinen: {s}")


def tarih_normalize_toplu():
    scraper = BaseScraper("temp", "temp")
    haberler = list(haberler_col.find({"yayin_tarihi": {"$exists": True, "$ne": None}}))
    print(f"\n📅 Tarih normalizasyonu: {len(haberler)} haber")
    d = 0
    for h in haberler:
        raw = h.get("yayin_tarihi", "")
        iso = scraper.tarih_normalize(raw)
        if iso and iso != raw:
            haberler_col.update_one({"_id": h["_id"]}, {"$set": {"yayin_tarihi": iso}})
            d += 1
    print(f"  ✅ {d} tarih duzeltildi.")


def ek_linkler_ekle():
    sonuc = haberler_col.update_many(
        {"ek_linkler": {"$exists": False}},
        {"$set": {"ek_linkler": []}}
    )
    print(f"\n🔗 {sonuc.modified_count} habere ek_linkler alani eklendi.")


if __name__ == "__main__":
    print("=" * 55)
    print("  Veritabani Guncelleme (drop etmeden)")
    print("=" * 55)
    siniflandirma_duzelt()
    tarih_normalize_toplu()
    ilce_alani_guncelle()
    ek_linkler_ekle()
    tum_haberleri_geocode_et()
    toplam = haberler_col.count_documents({})
    koordinatli = haberler_col.count_documents({"enlem": {"$ne": None}})
    print(f"\n  📊 Toplam: {toplam} | Koordinatli: {koordinatli}")




