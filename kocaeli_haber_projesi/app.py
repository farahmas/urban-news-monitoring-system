from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from database import haberler_col
from datetime import datetime, timedelta
from dotenv import load_dotenv
import sys
import os

load_dotenv()

app = Flask(__name__)
CORS(app)


GECERLI_TURLER = [
    "Trafik Kazası", "Yangın", "Elektrik Kesintisi",
    "Hırsızlık", "Kültürel Etkinlikler",
]


@app.route("/")
def index():
    google_maps_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    return render_template("index.html", google_maps_key=google_maps_key)


@app.route("/api/haberler", methods=["GET"])
def haberleri_getir():
    
    filtre = {
        "enlem": {"$ne": None},
        "boylam": {"$ne": None},
        "haber_turu": {"$in": GECERLI_TURLER},
        "gecersiz_tur": {"$ne": True},
        "kocaeli_disi": {"$ne": True}
    }

    
    tur = request.args.get("tur")
    if tur and tur != "Tümü":
        filtre["haber_turu"] = tur

   
    ilce = request.args.get("ilce")
    if ilce and ilce != "Tümü":
        filtre["ilce"] = ilce

    
    baslangic = request.args.get("baslangic")
    bitis = request.args.get("bitis")
    if baslangic or bitis:
        tarih_filtre = {}
        if baslangic:
            tarih_filtre["$gte"] = baslangic
        if bitis:
            tarih_filtre["$lte"] = bitis
        if tarih_filtre:
            filtre["yayin_tarihi"] = tarih_filtre

    
    haberler = list(haberler_col.find(
        filtre,
        {
            "_id": 0,
            "haber_basligi": 1,
            "haber_turu": 1,
            "konum_metni": 1,
            "ilce": 1,
            "enlem": 1,
            "boylam": 1,
            "yayin_tarihi": 1,
            "haber_sitesi": 1,
            "haber_linki": 1,
            "kaynak_listesi": 1,
            "ek_linkler": 1,
        }
    ).sort("yayin_tarihi", -1).limit(500))

    return jsonify({
        "toplam": len(haberler),
        "haberler": haberler
    })


@app.route("/api/istatistik", methods=["GET"])
def istatistik():
    
    ortak_filtre = {
        "gecersiz_tur": {"$ne": True},
        "kocaeli_disi": {"$ne": True},
        "haber_turu": {"$in": GECERLI_TURLER}
    }

    return jsonify({
        "toplam": haberler_col.count_documents(ortak_filtre),
        "koordinatli": haberler_col.count_documents({
            **ortak_filtre,
            "enlem": {"$ne": None},
            "boylam": {"$ne": None}
        }),
        "yangin": haberler_col.count_documents({
            **ortak_filtre,
            "haber_turu": "Yangın"
        }),
        "trafik": haberler_col.count_documents({
            **ortak_filtre,
            "haber_turu": "Trafik Kazası"
        }),
        "elektrik": haberler_col.count_documents({
            **ortak_filtre,
            "haber_turu": "Elektrik Kesintisi"
        }),
        "hirsizlik": haberler_col.count_documents({
            **ortak_filtre,
            "haber_turu": "Hırsızlık"
        }),
        "kulturel": haberler_col.count_documents({
            **ortak_filtre,
            "haber_turu": "Kültürel Etkinlikler"
        }),
    })

@app.route("/api/scrape", methods=["POST"])
def scrape_baslat():
    
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from scrapers.cagdas_scraper import CagdasKocaeliScraper
        from scrapers.ozgur_scraper import OzgurKocaeliScraper
        from scrapers.ses_scraper import SesKocaeliScraper
        from scrapers.yeni_scraper import YeniKocaeliScraper
        from scrapers.bizimyaka_scraper import BizimYakaScraper
        from geocoder.geocoder import tum_haberleri_geocode_et
        from processor.embedder import tum_haberleri_analiz_et

        scraperlar = [
            CagdasKocaeliScraper(),
            OzgurKocaeliScraper(),
            SesKocaeliScraper(),
            YeniKocaeliScraper(),
            BizimYakaScraper(),
        ]

        sayi_filtresi = {
            "gecersiz_tur": {"$ne": True},
            "kocaeli_disi": {"$ne": True},
            "haber_turu": {"$in": GECERLI_TURLER}
        }

        onceki_sayi = haberler_col.count_documents(sayi_filtresi)

        for scraper in scraperlar:
            try:
                scraper.scrape()
            except Exception as e:
                print(f"Scraper hatası ({scraper.site_adi}): {e}")

        tum_haberleri_geocode_et()
        tum_haberleri_analiz_et()

        yeni_sayi = haberler_col.count_documents(sayi_filtresi)

        return jsonify({
            "basarili": True,
            "mesaj": f"Scraping tamamlandı. {yeni_sayi - onceki_sayi} yeni haber eklendi. Toplam: {yeni_sayi}",
            "toplam": yeni_sayi
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "basarili": False,
            "mesaj": f"Hata: {str(e)}"
        }), 500


@app.route("/api/ilceler", methods=["GET"])
def ilceleri_getir():
   
    ilceler = haberler_col.distinct("ilce", {
        "gecersiz_tur": {"$ne": True},
        "kocaeli_disi": {"$ne": True},
        "haber_turu": {"$in": GECERLI_TURLER},
        "enlem": {"$ne": None},
        "boylam": {"$ne": None}
    })
    ilceler = [i for i in ilceler if i]
    ilceler.sort()
    return jsonify(ilceler)


if __name__ == "__main__":
    print("🚀 Kocaeli Haber Sistemi başlatılıyor...")
    print("📍 http://localhost:5000 adresini aç")
    app.run(debug=True, port=5000)


