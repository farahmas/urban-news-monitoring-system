"""
embedder.py

"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from database import haberler_col

MODEL_ADI = "paraphrase-multilingual-MiniLM-L12-v2"
BENZERLIK_ESIGI = 0.90  


_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        print("🤖 Embedding modeli yükleniyor...")
        _model = SentenceTransformer(MODEL_ADI)
        print("✅ Model hazır!")
    return _model


def embedding_olustur(metin):
    model = _get_model()
    return model.encode(metin, convert_to_numpy=True)


def benzerlik_hesapla(embedding1, embedding2):
    from sklearn.metrics.pairwise import cosine_similarity
    e1 = embedding1.reshape(1, -1)
    e2 = embedding2.reshape(1, -1)
    return float(cosine_similarity(e1, e2)[0][0])


def haberleri_birlestir(ana_id, benzer_haber):
    
    benzer_site = benzer_haber.get("haber_sitesi", "")
    benzer_link = benzer_haber.get("haber_linki", "")

    haberler_col.update_one(
        {"_id": ana_id},
        {
            "$addToSet": {
                "kaynak_listesi": benzer_site
            },
            "$push": {
                "ek_linkler": benzer_link
            }
        }
    )

    haberler_col.delete_one({"_id": benzer_haber["_id"]})


def tum_haberleri_analiz_et():
    
    print("\n🔍 Embedding benzerlik analizi başlıyor...")

    haberler = list(haberler_col.find(
        {},
        {"_id": 1, "haber_basligi": 1, "haber_icerigi": 1,
         "haber_sitesi": 1, "haber_linki": 1, "kaynak_listesi": 1}
    ))

    toplam = len(haberler)
    if toplam < 2:
        print("  Karşılaştırılacak yeterli haber yok.")
        return

    print(f"  Toplam {toplam} haber analiz edilecek...")

    model = _get_model()
    metinler = []
    for h in haberler:
        metin = h.get("haber_basligi", "") + " " + h.get("haber_icerigi", "")[:500]
        metinler.append(metin)

    print("  Embedding'ler oluşturuluyor...")
    embeddings = model.encode(metinler, convert_to_numpy=True, show_progress_bar=True)
    print(f"  ✅ {toplam} embedding oluşturuldu.")

    silinecekler = set()
    birlestirilen = 0

    print("  Benzerlik karşılaştırması yapılıyor...")
    for i in range(toplam):
        if haberler[i]["_id"] in silinecekler:
            continue

        for j in range(i + 1, toplam):
            if haberler[j]["_id"] in silinecekler:
                continue

            
            if haberler[i].get("haber_sitesi") == haberler[j].get("haber_sitesi"):
                continue

            benzerlik = benzerlik_hesapla(embeddings[i], embeddings[j])

            if benzerlik >= BENZERLIK_ESIGI:
                print(f"\n  🔗 Benzer haber bulundu! (benzerlik: {benzerlik:.2f})")
                print(f"     [{haberler[i]['haber_sitesi']}] {haberler[i]['haber_basligi'][:50]}")
                print(f"     [{haberler[j]['haber_sitesi']}] {haberler[j]['haber_basligi'][:50]}")

                haberleri_birlestir(haberler[i]["_id"], haberler[j])
                silinecekler.add(haberler[j]["_id"])
                birlestirilen += 1

    print(f"\n  📊 Analiz tamamlandı!")
    print(f"  Birleştirilen haber çifti: {birlestirilen}")
    print(f"  Kalan haber sayısı: {haberler_col.count_documents({})}")


if __name__ == "__main__":
    tum_haberleri_analiz_et()


