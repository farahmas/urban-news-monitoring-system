"""
veritabani_test.py 
"""
from database import haberler_col, geocache_col, db

def main():
    print("=" * 55)
    print("  Veritabanı Kontrol")
    print("=" * 55)
    try:
        db.command("ping")
        print("✅ MongoDB bağlantısı başarılı!")
    except Exception as e:
        print(f"❌ MongoDB hatası: {e}")
        return

    print(f"\n📊 haberler: {haberler_col.count_documents({})} kayıt")
    print(f"   geocache: {geocache_col.count_documents({})} kayıt")

    print("\n📰 Haber Türü Dağılımı:")
    for s in haberler_col.aggregate([{"$group": {"_id": "$haber_turu", "c": {"$sum": 1}}}, {"$sort": {"c": -1}}]):
        print(f"   {s['_id'] or 'Belirsiz'}: {s['c']}")

    print("\n🌐 Kaynak Dağılımı:")
    for s in haberler_col.aggregate([{"$group": {"_id": "$haber_sitesi", "c": {"$sum": 1}}}, {"$sort": {"c": -1}}]):
        print(f"   {s['_id']}: {s['c']}")

    print("\n📍 İlçe Dağılımı:")
    for s in haberler_col.aggregate([{"$group": {"_id": "$ilce", "c": {"$sum": 1}}}, {"$sort": {"c": -1}}]):
        print(f"   {s['_id'] or 'Belirsiz'}: {s['c']}")

    t = haberler_col.count_documents({})
    k = haberler_col.count_documents({"enlem": {"$ne": None}})
    o = (k/t*100) if t > 0 else 0
    print(f"\n🗺️  Koordinatlı: {k}/{t} ({o:.1f}%)")

    print("\n🔗 Birleştirilmiş haberler:")
    for h in haberler_col.find({"kaynak_listesi.1": {"$exists": True}}, {"haber_basligi": 1, "kaynak_listesi": 1}).limit(5):
        print(f"   {h['haber_basligi'][:50]}... → {', '.join(h.get('kaynak_listesi', []))}")

    print("\n📋 Son 5 Haber:")
    for i, h in enumerate(haberler_col.find().sort("_id", -1).limit(5), 1):
        enlem = h.get("enlem")
        coord = f"({enlem:.4f})" if enlem else "(yok)"
        print(f"   {i}. [{h.get('haber_turu','?')}] {h.get('haber_basligi','')[:45]}... | {h.get('ilce','?')} {coord}")

if __name__ == "__main__":
    main()


