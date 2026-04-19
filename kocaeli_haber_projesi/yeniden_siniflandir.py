from database import haberler_col
from scrapers.base_scraper import BaseScraper, ONCELIK_SIRASI

scraper = BaseScraper("temp", "temp")

degisenler = 0
ayni_kalanlar = 0
tur_yok = 0

print("=" * 65)
print("  Mevcut Haberleri Yeni Kuralla Yeniden Sınıflandırma")
print("=" * 65)

for h in haberler_col.find({}, {
    "_id": 1,
    "haber_basligi": 1,
    "haber_icerigi": 1,
    "haber_turu": 1
}):
    baslik = h.get("haber_basligi", "")
    icerik = h.get("haber_icerigi", "")
    eski_tur = h.get("haber_turu")
    yeni_tur = scraper.haber_turunu_bul(baslik, icerik)

    if yeni_tur is None:
        haberler_col.update_one(
            {"_id": h["_id"]},
            {"$set": {"haber_turu": None}}
        )
        tur_yok += 1
        print(f"  ⚠️ Tür kaldırıldı: {baslik[:80]}")
        continue

    if yeni_tur != eski_tur:
        haberler_col.update_one(
            {"_id": h["_id"]},
            {"$set": {"haber_turu": yeni_tur}}
        )
        degisenler += 1
        print(f"  ✏️ {eski_tur} → {yeni_tur} | {baslik[:80]}")
    else:
        ayni_kalanlar += 1

print("\n" + "=" * 65)
print(f"Değişen: {degisenler}")
print(f"Aynı kalan: {ayni_kalanlar}")
print(f"Tür bulunamayan: {tur_yok}")

print("\nYeni dağılım:")
for tur in ONCELIK_SIRASI:
    sayi = haberler_col.count_documents({"haber_turu": tur})
    print(f"  {tur}: {sayi}")

print(f"\nToplam kayıt: {haberler_col.count_documents({})}")
print("=" * 65)














