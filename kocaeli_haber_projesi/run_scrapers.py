"""
run_scrapers.py

"""

from scrapers.cagdas_scraper import CagdasKocaeliScraper
from scrapers.ozgur_scraper import OzgurKocaeliScraper
from scrapers.ses_scraper import SesKocaeliScraper
from scrapers.yeni_scraper import YeniKocaeliScraper
from scrapers.bizimyaka_scraper import BizimYakaScraper
from geocoder.geocoder import tum_haberleri_geocode_et
from processor.embedder import tum_haberleri_analiz_et
from database import haberler_col


def hepsini_tara():
    scraperlar = [
        CagdasKocaeliScraper(),
        OzgurKocaeliScraper(),
        SesKocaeliScraper(),
        YeniKocaeliScraper(),
        BizimYakaScraper(),
    ]

    print("=" * 55)
    print("  Kocaeli Haber Sistemi — Scraping Başlıyor")
    print("=" * 55)

    onceki = haberler_col.count_documents({})

    for scraper in scraperlar:
        try:
            scraper.scrape()
        except Exception as e:
            print(f"  ❌ {scraper.site_adi} hatası: {e}")

    print("\n" + "=" * 55)
    print("  Geocoding başlıyor...")
    print("=" * 55)
    tum_haberleri_geocode_et()

    print("\n" + "=" * 55)
    print("  Benzerlik analizi başlıyor...")
    print("=" * 55)
    tum_haberleri_analiz_et()

    sonraki = haberler_col.count_documents({})
    print("\n" + "=" * 55)
    print(f"  ✅ Tamamlandı! Eklenen: {sonraki - onceki} | Toplam: {sonraki}")
    print("=" * 55)


if __name__ == "__main__":
    hepsini_tara()






