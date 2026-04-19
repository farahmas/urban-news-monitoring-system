from database import haberler_col

for h in haberler_col.find().sort("_id", -1).limit(12):
    print("-" * 70)
    print("BAŞLIK:", h.get("haber_basligi", ""))
    print("TÜR   :", h.get("haber_turu"))
    print("İLÇE  :", h.get("ilce"))
    print("KONUM :", h.get("konum_metni"))












    