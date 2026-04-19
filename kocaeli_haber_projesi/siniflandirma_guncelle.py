"""
siniflandirma_guncelle.py

"""
from database import haberler_col
from scrapers.base_scraper import BaseScraper, ONCELIK_SIRASI, DIGER_SEHIRLER

scraper = BaseScraper("temp", "temp")
guncellenen = 0
silinen = 0
kocaeli_disi = 0

for h in haberler_col.find({}):
    baslik = h.get('haber_basligi', '')
    icerik = h.get('haber_icerigi', '')
    tam_metin = (baslik + " " + icerik).lower()

    
    ilce = scraper.ilce_bul(baslik + " " + icerik)
    kocaeli_var = "kocaeli" in tam_metin
    baska_sehir = False
    for sehir in DIGER_SEHIRLER:
        if sehir in tam_metin:
            baska_sehir = True
            break

    if baska_sehir and not ilce and not kocaeli_var:
        haberler_col.delete_one({'_id': h['_id']})
        kocaeli_disi += 1
        print(f"  🗑️ Kocaeli dışı silindi: {baslik[:50]}...")
        continue

   
    yeni_tur = scraper.haber_turunu_bul(baslik, icerik)
    eski_tur = h.get('haber_turu')

    if yeni_tur and yeni_tur != eski_tur:
        haberler_col.update_one({'_id': h['_id']}, {'$set': {'haber_turu': yeni_tur}})
        guncellenen += 1
        print(f"  ✏️ {eski_tur} → {yeni_tur}: {baslik[:50]}...")
    elif not yeni_tur:
        haberler_col.delete_one({'_id': h['_id']})
        silinen += 1
        print(f"  🗑️ 5 türe girmiyor, silindi: {baslik[:50]}...")

print(f'\nGüncellenen: {guncellenen} | Silinen: {silinen} | Kocaeli dışı: {kocaeli_disi}')
print('\nYeni dağılım:')
for tur in ONCELIK_SIRASI:
    sayi = haberler_col.count_documents({'haber_turu': tur})
    print(f'  {tur}: {sayi}')
print(f'  TOPLAM: {haberler_col.count_documents({})}')




