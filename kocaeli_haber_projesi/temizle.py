from database import haberler_col

SILINECEK = [
    "Adapazarı Belediye Başkanı",
    "Uşak Belediyesi",
    "Kandıra GB Belediyespor",
    "CEDİT KENTSEL DÖNÜŞÜM",
    "SMA Hastası Talha",
    "Çöp Kamyonu Dönemi",
    "Arıcılara Üretim Desteği",
    "Liman Devlerinden Kritik",
    "Ormancılar Haftası",
    "Ticaret Odası heyeti",
    "Gençler sordu",
    "kütüphaneleri 2 yılda",
    "aziz şehidimize",
    "Büyükakın kalem kalem",
    "Ziraat Odası Başkanı",
    "Elektronik Atıklar",
    "Cevher Çocuk Projesi",
    "aileler sporda buluşuyor",
]

silinen = 0
for kelime in SILINECEK:
    sonuc = haberler_col.delete_many({"haber_basligi": {"$regex": kelime}})
    if sonuc.deleted_count > 0:
        print(f"  🗑️ Silindi ({sonuc.deleted_count}): ...{kelime}...")
        silinen += sonuc.deleted_count

print(f"\nToplam silinen: {silinen}")
print(f"Kalan: {haberler_col.count_documents({})}")

print("\nYeni dağılım:")
for tur in ["Trafik Kazası", "Yangın", "Elektrik Kesintisi", "Hırsızlık", "Kültürel Etkinlikler"]:
    print(f"  {tur}: {haberler_col.count_documents({'haber_turu': tur})}")


