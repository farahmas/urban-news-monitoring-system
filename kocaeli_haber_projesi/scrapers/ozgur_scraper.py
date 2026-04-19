import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from urllib.parse import urljoin
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper


class OzgurKocaeliScraper(BaseScraper):

    def __init__(self):
        super().__init__(
            site_adi="Özgür Kocaeli",
            ana_url="https://www.ozgurkocaeli.com.tr/"
        )

    def haber_detay_cek(self, url):
        html = self.sayfayi_indir(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        h1 = soup.find("h1")
        baslik = self.metin_temizle(h1.text) if h1 else ""
        if not baslik or len(baslik) < 10:
            return None

        icerik_alani = (
            soup.find("article") or
            soup.find("div", class_="content") or
            soup.find("div", class_="haber-detay") or
            soup.find("div", class_="single-content") or
            soup.find("div", class_="entry-content")
        )
        if icerik_alani:
            paragraflar = [p.text.strip() for p in icerik_alani.find_all("p") if len(p.text.strip()) > 40]
        else:
            paragraflar = [p.text.strip() for p in soup.find_all("p") if len(p.text.strip()) > 40]

        icerik = self.metin_temizle(" ".join(paragraflar))
        if len(icerik) < 50:
            return None

        tarih = self.tarih_cikart(soup, html)

        kategori = self.haber_turunu_bul(baslik, icerik)
        if not kategori:
            return None

        konum_metni = self.konum_bul(baslik + " " + icerik)

        return {
            "haber_basligi": baslik,
            "haber_icerigi": icerik,
            "yayin_tarihi": tarih,
            "haber_linki": url,
            "haber_sitesi": self.site_adi,
            "haber_turu": kategori,
            "konum_metni": konum_metni,
            "koordinatlar": None,
            "enlem": None,
            "boylam": None,
            "kaynak_listesi": [self.site_adi],
            "ek_linkler": [],
        }

    def scrape(self):
        print(f"\n🔍 {self.site_adi} taranıyor...")
        html = self.sayfayi_indir(self.ana_url)
        if not html:
            print("  Ana sayfa indirilemedi.")
            return

        soup = BeautifulSoup(html, "html.parser")

        linkler = set()
        for a in soup.find_all("a", href=True):
            link = a["href"]
            tam_link = urljoin(self.ana_url, link)
            if (
                tam_link.startswith(self.ana_url) and
                any(k in link for k in ["/haber/", "/guncel/", "/son-dakika/", "/?p="]) and
                len(link) > 15
            ):
                linkler.add(tam_link)

        bulunan = 0
        kaydedilen = 0

        for tam_link in linkler:
            veri = self.haber_detay_cek(tam_link)
            if veri:
                bulunan += 1
                if self.haber_yeni_mi(veri["yayin_tarihi"]):
                    if self.veritabanina_kaydet(veri):
                        kaydedilen += 1

        print(f"  📊 {self.site_adi}: Bulunan={bulunan} | Kaydedilen={kaydedilen}")


if __name__ == "__main__":
    scraper = OzgurKocaeliScraper()
    scraper.scrape()


