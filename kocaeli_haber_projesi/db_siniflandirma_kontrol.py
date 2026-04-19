from database import haberler_col
from scrapers.base_scraper import BaseScraper

scraper = BaseScraper("test", "test")

print("=" * 80)
print("MEVCUT DB ÜZERİNDE SINIFLANDIRMA KONTROLÜ")
print("=" * 80)

toplam = 0
ayni = 0
farkli = 0
none_olan = 0

for h in haberler_col.find({}, {
    "_id": 1,
    "haber_basligi": 1,
    "haber_icerigi": 1,
    "haber_turu": 1,
    "gecersiz_tur": 1,
    "kocaeli_disi": 1
}):
    toplam += 1

    baslik = h.get("haber_basligi", "")
    icerik = h.get("haber_icerigi", "")
    eski = h.get("haber_turu")
    yeni = scraper.haber_turunu_bul(baslik, icerik, debug=False)

    if yeni is None:
        none_olan += 1
        print(f"\n[None]")
        print(f"ESKİ   : {eski}")
        print(f"BAŞLIK : {baslik}")
        print("-" * 80)
        continue

    if yeni == eski:
        ayni += 1
    else:
        farkli += 1
        print(f"\n[FARKLI]")
        print(f"ESKİ   : {eski}")
        print(f"YENİ   : {yeni}")
        print(f"BAŞLIK : {baslik}")
        print("-" * 80)

print("\n" + "=" * 80)
print(f"Toplam kayıt : {toplam}")
print(f"Aynı kalan   : {ayni}")
print(f"Farklı çıkan : {farkli}")
print(f"None çıkan   : {none_olan}")
print("=" * 80)






