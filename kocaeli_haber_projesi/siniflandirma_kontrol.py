from database import haberler_col

TURLER = [
    "Trafik Kazası",
    "Yangın",
    "Elektrik Kesintisi",
    "Hırsızlık",
    "Kültürel Etkinlikler",
]

print("=" * 70)
print("Sınıflandırma Kontrolü")
print("=" * 70)

for tur in TURLER:
    print(f"\n### {tur} ###")
    for i, h in enumerate(
        haberler_col.find(
            {"haber_turu": tur, "gecersiz_tur": {"$ne": True}},
            {"haber_basligi": 1, "haber_icerigi": 1}
        ).limit(10),
        1
    ):
        print(f"{i}. {h.get('haber_basligi', '')}")