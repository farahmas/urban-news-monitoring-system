import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import json
import time
import random
import unicodedata
from database import haberler_col
from processor.news_classifier import semantic_kategori_skorlari


KATEGORI_KURALLARI = {
    "Trafik Kazası": {
        "guclu": [
            "trafik kazası", "zincirleme kaza", "trafik kazasında",
            "motosiklet kazası", "otobüs kazası", "ölümlü kaza",
            "maddi hasarlı kaza", "kavşakta kaza", "feci kaza",
            "iki araç çarpıştı", "otomobil ile motosiklet çarpıştı",
            "tır ile otomobil çarpıştı", "kamyondan düşen tomruk",
            "otomobile saplandı", "direksiyon hakimiyetini kaybetti",
            "kontrolden çıktı", "yayaya çarptı", "yol ulaşıma kapandı"
        ],
        "orta": [
            "çarpıştı", "takla attı", "şarampole",
            "kaza meydana", "tır devrildi",
            "araç takla", "kazada yaralandı",
            "bariyere çarptı", "refüje çarptı",
            "kamyon devrildi", "otomobil devrildi"
        ],
        "zayif": [],
        "kara_liste": [
            "iş kazası", "depremzede", "siyasi kaza", "kazanan",
            "turnuva", "yarışma", "müsabaka",
            "sabiha gökçen hattı", "yolcular yolda kaldı", "kriz"
        ],
    },

    "Yangın": {
        "guclu": [
            "yangın çıktı", "çıkan yangın", "ev yangını",
            "fabrika yangını", "çatı yangını", "orman yangını",
            "otluk yangını", "baca yangını", "yangına müdahale",
            "itfaiye ekipleri müdahale", "yangın söndürüldü",
            "alevlere teslim oldu", "alev alev yandı",
            "yangın kontrol altına alındı", "soğutma çalışması yapıldı",
            "olay yerine itfaiye ekipleri sevk edildi",
            "şofben alev aldı", "araç alev aldı"
        ],
        "orta": [
            "ev yandı", "fabrika yandı",
            "araç alev aldı", "yangın paniği",
            "bacasında yangın"
        ],
        "zayif": [],
        "kara_liste": [
            "davasında", "davasının", "davası", "yargılandığı",
            "sanık", "sanıklar", "tutuklu", "tahliye",
            "mahkeme", "duruşma", "savunma", "müşteki",
            "ceza infaz", "savcı",
            "saldırı", "tabancayla", "ateş açıldı", "silahlı",
            "uyuşturucu", "narkotik", "operasyonu",
            "baskın yapılan", "zabıta", "denetim",
            "ağaçlandırma", "fidan", "destek"
        ],
    },

    "Elektrik Kesintisi": {
        "guclu": [
            "elektrik kesintisi", "elektrikler kesilecek", "planlı kesinti",
            "elektrik verilmeyecek", "elektrik kesilecek",
            "elektrik kesileceği", "enerji kesintisi",
            "elektriksiz kalacak", "elektrik kesinti programı",
        ],
        "orta": [
            "sedaş", "trafo arızası", "bakım çalışması",
            "enerji verilemeyecek",
        ],
        "zayif": [
            "kesinti", "trafo",
        ],
        "kara_liste": [
            "elektrik faturası", "elektrik akımı", "elektrikli araç",
        ],
    },

    "Hırsızlık": {
        "guclu": [
            "hırsızlık", "hırsız yakalandı", "hırsız tutuklandı",
            "hırsızlık şüphelisi", "ev soyuldu", "araç çalındı",
            "kapkaç", "gasp", "soygun", "kablo hırsızlığı",
            "kablo vurgunu", "çalıntı motosiklet", "çalıntı araç"
        ],
        "orta": [
            "kasayı çaldı", "yankesici", "çalıntı çıktı"
        ],
        "zayif": [],
        "kara_liste": [
            "fikri mülkiyet", "eser çalındı gibi", "şarkıyı çaldı",
            "karakol", "polis öğrenci buluşması", "öğrenci buluşması",
            "dolandırıldı", "dolandırıcılık", "elektrik akımı",
            "kaza", "kazaya", "otomobil devrildi", "tır dorsesi",
            "yola dökülen atıklar", "zincirleme kaza"
        ],
    },

    "Kültürel Etkinlikler": {
        "guclu": [
            "konser düzenlendi", "konser verildi",
            "tiyatro oyunu", "tiyatro gösterimi",
            "sergi açıldı", "sergi düzenlendi",
            "festival düzenlendi", "müzik festivali",
            "resim sergisi", "kitap fuarı", "kültürel etkinlik",
            "söyleşi düzenlendi", "bilim söyleşisi",
        ],
        "orta": [
            "sahne aldı", "sahneye çıktı", "dans gösterisi",
            "müzik dinletisi", "kutlama töreni",
            "etkinlik düzenlendi", "panel düzenlendi",
            "sanat sergisi", "kültür merkezi etkinlik",
        ],
        "zayif": [
            "konser", "festival", "sergi", "tiyatro"
        ],
        "kara_liste": [
            "maç", "gol", "penaltı", "lig", "spor", "futbol", "basketbol",
            "belediyespor", "deplasman", "galatasaray", "fenerbahçe", "beşiktaş",
            "şampiyonluk", "turnuva", "yarı final", "final", "milli takım",
            "antrenör", "karşılaşma", "skor", "puan",

            "belediye başkanı", "meclis", "operasyon", "rüşvet",
            "istifa", "seçim", "parti", "milletvekili", "vali",
            "kentsel dönüşüm", "altyapı", "çöp kamyonu",
            "ihale", "proje sunumu", "protokol",

            "hastası", "tedavi", "ameliyat", "sma",

            "uyuşturucu", "narkotik", "gözaltı", "saldırı",
            "cinayet", "ateş açıldı", "tabancayla",

            "ziraat odası", "ticaret odası", "arıcılara", "fındık fiyat",
            "kamera", "cctv", "zabıta", "denetim", "baskın yapılan",
        ],
    },
}



ONCELIK_SIRASI = [
    "Trafik Kazası",
    "Yangın",
    "Elektrik Kesintisi",
    "Hırsızlık",
    "Kültürel Etkinlikler",
]

AYLAR = {
    "Ocak": "01", "Şubat": "02", "Mart": "03", "Nisan": "04",
    "Mayıs": "05", "Haziran": "06", "Temmuz": "07", "Ağustos": "08",
    "Eylül": "09", "Ekim": "10", "Kasım": "11", "Aralık": "12"
}

ILCELER = [
    "İzmit", "Gebze", "Darıca", "Gölcük", "Körfez", "Derince",
    "Çayırova", "Kartepe", "Başiskele", "Karamürsel", "Kandıra", "Dilovası"
]

DIGER_SEHIRLER = [
    
    "adana", "adıyaman", "afyonkarahisar", "ağrı", "amasya", "ankara",
    "antalya", "artvin", "aydın", "balıkesir", "bilecik", "bingöl",
    "bitlis", "bolu", "burdur", "bursa", "çanakkale", "çankırı",
    "çorum", "denizli", "diyarbakır", "edirne", "elazığ", "erzincan",
    "erzurum", "eskişehir", "gaziantep", "giresun", "gümüşhane",
    "hakkari", "hatay", "ısparta", "mersin", "istanbul", "izmir",
    "kars", "kastamonu", "kayseri", "kırklareli", "kırşehir", "konya",
    "kütahya", "malatya", "manisa", "kahramanmaraş", "mardin", "muğla",
    "muş", "nevşehir", "niğde", "ordu", "rize", "sakarya", "samsun",
    "siirt", "sinop", "sivas", "tekirdağ", "tokat", "trabzon",
    "tunceli", "şanlıurfa", "uşak", "van", "yozgat", "zonguldak",
    "aksaray", "bayburt", "karaman", "kırıkkale", "batman", "şırnak",
    "bartın", "ardahan", "ığdır", "yalova", "karabük", "kilis",
    "osmaniye", "düzce",

    
    "adalar", "arnavutköy", "ataşehir", "avcılar", "bağcılar", "bahçelievler",
    "bakırköy", "başakşehir", "bayrampaşa", "beşiktaş", "beykoz", "beylikdüzü",
    "beyoğlu", "büyükçekmece", "çekmeköy", "esenler", "esenyurt", "eyüpsultan",
    "fatih", "gaziosmanpaşa", "güngören", "kadıköy", "kağıthane", "kartal",
    "küçükçekmece", "maltepe", "pendik", "sancaktepe", "sarıyer", "silivri",
    "sultanbeyli", "sultangazi", "şile", "şişli", "tuzla", "ümraniye",
    "üsküdar", "zeytinburnu",

    
    "altındağ", "ayaş", "bala", "beypazarı", "çamlıdere", "çankaya",
    "elmadağ", "etimesgut", "evren", "gölbaşı", "güdül", "haymana",
    "kahramankazan", "kalecik", "keçiören", "kızılcahamam", "mamak",
    "nallıhan", "polatlı", "pursaklar", "sincan", "şereflikoçhisar", "yenimahalle",

    
    "aliağa", "balçova", "bayındır", "bayraklı", "bergama", "bornova",
    "buca", "çeşme", "çiğli", "dikili", "foça", "gaziemir", "güzelbahçe",
    "karabağlar", "karaburun", "karşıyaka", "kemalpaşa", "kinik", "kiraz",
    "konak", "menderes", "menemen", "narlıdere", "ödemiş", "seferihisar",
    "selçuk", "tire", "torbalı", "urla",

    
    "büyükorhan", "gemlik", "gürsu", "harmancık", "inegöl", "iznik",
    "karacabey", "keles", "kestel", "mudanya", "mustafakemalpaşa",
    "nilüfer", "orhaneli", "orhangazi", "osmangazi", "yenişehir", "yıldırım",

    
    "adapazarı", "akyazı", "arifiye", "erenler", "ferizli", "geyve",
    "hendek", "karapürçek", "karasu", "kaynarca", "kocaali", "pamukova",
    "sapanca", "serdivan", "söğütlü", "taraklı",

    
    "çerkezköy", "çorlu", "ergene", "hayrabolu", "kapaklı", "malkara",
    "marmaraereğlisi", "muratlı", "saray", "süleymanpaşa", "şarköy",

    
    "altıeylül", "ayvalık", "balya", "bandırma", "bigadiç", "burhaniye",
    "dursunbey", "edremit", "erdek", "gönen", "havran", "ivrindi",
    "karesi", "kepsut", "manyas", "marmara", "savaştepe", "sındırgı",
    "susurluk",

    
    "ahmetli", "akhisar", "alaşehir", "demirci", "gölmarmara", "gördes",
    "kırkağaç", "köprübaşı", "kula", "salihli", "saruhanlı", "selendi",
    "soma", "şehzadeler", "turgutlu", "yunusemre",

    
    "bozdoğan", "buharkent", "çine", "didim", "efeler", "germencik",
    "incirliova", "karacasu", "karpuzlu", "koçarlı", "köşk", "kuşadası",
    "kuyucak", "nazilli", "söke", "sultanhisar", "yenipazar",

    
    "bodrum", "dalaman", "datça", "fethiye", "kavaklıdere", "köyceğiz",
    "marmaris", "menteşe", "milas", "ortaca", "seydikemer", "ula",
    "yatagan",

    
    "aksu", "alanya", "demre", "döşemealtı", "elmali", "finike", "gazipaşa",
    "gündoğmuş", "ibradı", "kaş", "kemer", "kepez", "konyaaltı", "korkuteli",
    "kumluca", "manavgat", "muratpaşa", "serik",

   
    "akkışla", "bünyan", "develi", "felahiye", "hacılar", "incesu",
    "kocasinan", "melikgazi", "özvatan", "pınarbaşı", "sarız", "talas",
    "tomarza", "yahyalı", "yeşilhisar",

   
    "ahırlı", "akören", "akseki", "akşehir", "altınekin", "beyşehir",
    "bozkır", "cihanbeyli", "çeltik", "çumra", "derbent", "derebucak",
    "doğanhisar", "emirgazi", "ereğli", "güneysınır", "hadim", "halkapınar",
    "hüyük", "ilgın", "kadınhanı", "karapınar", "kulu", "meram",
    "selçuklu", "seydişehir", "taşkent", "tuzlukçu", "yalıhüyük", "yunak",

   
    "akdeniz", "anamur", "aydıncık", "bozyazı", "çamlıyayla", "erdemli",
    "gülnar", "mezitli", "mut", "silifke", "tarsus", "toroslar", "yenişehir",

   
    "aladağ", "ceyhan", "çukurova", "feke", "imamoğlu", "karaisalı",
    "karataş", "kozan", "pozantı", "saimbeyli", "sarıçam", "seyhan",
    "tufanbeyli", "yumurtalık", "yüreğir",

    
    "araban", "islahiye", "karkamış", "nizip", "nurdağı", "oğuzeli",
    "şahinbey", "şehitkamil", "yavuzeli",

    
    "altınözü", "antakya", "arsuz", "belen", "defne", "dörtyol", "erzin",
    "hassa", "iskenderun", "kırıkhan", "kumlu", "payas", "reyhanlı",
    "samandağ", "yayladağı",

    
    "alaçam", "asarcık", "atakum", "ayvacık", "bafra", "canik", "çarşamba",
    "havza", "ilkadım", "kavak", "ladik", "salıpazarı", "tekkeköy",
    "terme", "vezirköprü", "yakakent",

    
    "akçaabat", "araklı", "arsin", "beşikdüzü", "çarşıbaşı", "çaykara",
    "dernekpazarı", "düzköy", "hayrat", "köprübaşı", "maçka", "of",
    "ortahisar", "sürmene", "şalpazarı", "tonya", "vakfıkebir", "yomra",

    
    "alpu", "beylikova", "çifteler", "günyüzü", "han", "inönü", "mahmudiye",
    "mihalgazi", "mihalıççık", "odunpazarı", "sarıcakaya", "seyitgazi",
    "sivrihisar", "tepebaşı",

   
    "merkez", "merkezefendi", "ilkadım", "ortahisar", "seyhan", "çankaya",
    "konak", "osmangazi", "selçuklu", "şahinbey", "şehitkamil", "muratpaşa",
    "kepez", "nilüfer", "kadıköy", "beşiktaş", "üsküdar", "fatih"
]


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
]


class BaseScraper:

    def __init__(self, site_adi, ana_url):
        self.site_adi = site_adi
        self.ana_url = ana_url

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })


    def sayfayi_indir(self, url):
        time.sleep(random.uniform(2.0, 4.0))

        
        self.session.headers["User-Agent"] = random.choice(USER_AGENTS)

        try:
            cevap = self.session.get(url, timeout=20)
            cevap.raise_for_status()
            cevap.encoding = cevap.apparent_encoding
            return cevap.text

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response is not None else "?"
            print(f"  ⚠️  HTTP hatası ({url[:60]}) [{status_code}]: {e}")

            if e.response is not None and e.response.status_code == 429:
                print("  ⏳ Rate limit algılandı, 15 saniye bekleniyor...")
                time.sleep(15)
                try:
                    cevap = self.session.get(url, timeout=20)
                    cevap.raise_for_status()
                    cevap.encoding = cevap.apparent_encoding
                    return cevap.text
                except Exception as e2:
                    print(f"  ⚠️  Tekrar deneme başarısız ({url[:60]}): {e2}")
                    return None

            return None

        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  İndirme hatası ({url[:60]}): {e}")
            return None

    def metin_temizle(self, metin):
        if not metin:
            return ""
        metin = re.sub(r'<[^>]+>', ' ', metin)
        metin = re.sub(r'[^\w\s.,!?;:\'\"()\-–/]', ' ', metin)
        metin = re.sub(r'\s+', ' ', metin).strip()
        metin = unicodedata.normalize("NFC", metin)
        return metin
    

    def _metin_siniflandirma_icin_hazirla(self, baslik, icerik):
        metin = f"{baslik} {icerik}".lower()
        metin = unicodedata.normalize("NFC", metin)
        metin = re.sub(r"\s+", " ", metin).strip()
        return metin
    

    def _ifade_say(self, metin, ifade):
        pattern = r'(?<!\w)' + re.escape(ifade) + r'(?!\w)'
        return len(re.findall(pattern, metin, flags=re.IGNORECASE))


    def _kategori_skoru_hesapla(self, baslik, icerik, kurallar):
        skor = 0

        for ifade in kurallar.get("guclu", []):
            skor += self._ifade_say(baslik, ifade) * 8
            skor += self._ifade_say(icerik, ifade) * 5

        for ifade in kurallar.get("orta", []):
            skor += self._ifade_say(baslik, ifade) * 5
            skor += self._ifade_say(icerik, ifade) * 3

        for ifade in kurallar.get("zayif", []):
            skor += self._ifade_say(baslik, ifade) * 2
            skor += self._ifade_say(icerik, ifade) * 1

        for ifade in kurallar.get("kara_liste", []):
            skor -= self._ifade_say(baslik, ifade) * 6
            skor -= self._ifade_say(icerik, ifade) * 4

        return skor
    


    def _kategori_on_kosulu_saglandi_mi(self, kategori, baslik, icerik):
        metin = f"{baslik} {icerik}".lower()

        if kategori == "Trafik Kazası":
            kaza_ifadeleri = [
                "kaza", "kazası", "kazada", "trafik kazası", "zincirleme kaza",
                "çarpıştı", "çarpışma", "takla attı", "şarampole", "devrildi",
                "bariyere çarptı", "refüje çarptı", "yol kapandı",
                "otomobile saplandı", "kontrolden çıktı", "yayaya çarptı"
            ]

            arac_ifadeleri = [
                "trafik", "araç", "sürücü", "otomobil", "motosiklet", "tır",
                "kamyon", "kamyonet", "otobüs", "minibüs", "servis aracı"
            ]

            yol_ifadeleri = [
                "yol", "otoyol", "tem", "d-100", "d100", "d-130", "d130",
                "d-605", "d605", "d-650", "d650", "gişe", "kavşak", "köprü"
            ]

            yasak = [
                "operasyon", "change operasyonu", "siber operasyon",
                "ceset bulundu", "bahçesinde ceset", "sağlık ocağı",
                "cinayet", "gözaltı", "mahkeme", "şüpheli", "uyuşturucu",
                "turnuva", "yarışma", "müsabaka",
                "sabiha gökçen hattı", "yolcular yolda kaldı", "kriz"
            ]

            kaza_var = any(k in metin for k in kaza_ifadeleri)
            arac_var = any(k in metin for k in arac_ifadeleri)
            yol_var = any(k in metin for k in yol_ifadeleri)
            yasak_var = any(k in metin for k in yasak)

            return kaza_var and (arac_var or yol_var) and not yasak_var

        if kategori == "Yangın":
            zorunlu = [
                "yangın", "yangın çıktı", "yangına müdahale",
                "itfaiye", "alev aldı", "şofben alev aldı",
                "ev yangını", "fabrika yangını"
            ]
            yasak = [
                "yangın davası", "mahkeme", "sanık", "tahliye",
                "ağaçlandırma", "fidan", "destek", "yanmıştı"
            ]
            return any(k in metin for k in zorunlu) and not any(k in metin for k in yasak)

        if kategori == "Elektrik Kesintisi":
            zorunlu = [
                "elektrik kesintisi", "elektrikler kesilecek",
                "elektrik verilmeyecek", "elektriksiz kalacak",
                "planlı kesinti", "trafo arızası"
            ]
            return any(k in metin for k in zorunlu)

        if kategori == "Hırsızlık":
            guclu_hirsizlik = [
                "hırsızlık", "hırsız", "çalıntı", "kapkaç", "soygun", "gasp",
                "ev soyuldu", "araç çalındı", "kablo hırsızlığı", "kablo vurgunu"
            ]
            yasak = [
                "sinema", "film", "cinayet", "cesedi", "mahkemede",
                "siber operasyon", "change operasyonu", "uyuşturucu", "kaçakçılık",
                "karakol", "polis öğrenci buluşması", "öğrenci buluşması",
                "dolandırıldı", "dolandırıcılık", "elektrik akımı",
                "kaza", "otomobil", "tır", "zincirleme"
            ]
            eslesme_sayisi = sum(1 for k in guclu_hirsizlik if k in metin)
            return eslesme_sayisi >= 1 and not any(k in metin for k in yasak)

        if kategori == "Kültürel Etkinlikler":
            metin = f"{baslik} {icerik}".lower()

            return (
                (
                    "kütüphane" in metin or
                    "kütüphaneler" in metin or
                    "yaşayan kütüphaneler" in metin or
                    "kütüphane haftası" in metin or
                    "festival" in metin or
                    "sergi" in metin or
                    "tiyatro" in metin or
                    "konser" in metin or
                    "söyleşi" in metin or
                    "dinleti" in metin or
                    "etkinlik" in metin or
                    "program" in metin or
                    "atölye" in metin or
                    "konferans salonu" in metin
                )
                and "maç" not in metin
                and "belediyespor" not in metin
                and "skor" not in metin
                and "puan" not in metin
                and "operasyon" not in metin
                and "gözaltı" not in metin
                and "mahkeme" not in metin
                and "cinayet" not in metin
                and "yangın" not in metin
                and "hırsızlık" not in metin
            )

        return False
    
    def haber_turunu_bul_semantic(self, baslik, icerik, debug=False):
        metin = f"{baslik} {icerik[:500]}".strip()
        if not metin:
            return None, {}

        skorlar = semantic_kategori_skorlari(metin)

        sirali = sorted(skorlar.items(), key=lambda x: x[1], reverse=True)
        en_iyi_kategori, en_iyi_skor = sirali[0]
        ikinci_skor = sirali[1][1] if len(sirali) > 1 else -1.0

        if debug:
            print(f"  🤖 Semantic sıralı skorlar: {sirali}")

        
        if en_iyi_skor < 0.45:
            return None, skorlar

        
        if (en_iyi_skor - ikinci_skor) < 0.05:
            return None, skorlar

        return en_iyi_kategori, skorlar
            

    def haber_turunu_bul_rule_based(self, baslik, icerik, debug=False):
        baslik_hazir = self._metin_siniflandirma_icin_hazirla(baslik, "")
        icerik_hazir = self._metin_siniflandirma_icin_hazirla("", icerik)

        skorlar = {}
        for kategori, kurallar in KATEGORI_KURALLARI.items():
            skorlar[kategori] = self._kategori_skoru_hesapla(
                baslik_hazir, icerik_hazir, kurallar
            )

        if debug:
            print(f"  🔎 Rule skorları: {skorlar}")

        if not skorlar:
            return None

        sirali = sorted(skorlar.items(), key=lambda x: x[1], reverse=True)

        for kategori, skor in sirali:
            if skor < 4:
                continue

            if self._kategori_on_kosulu_saglandi_mi(kategori, baslik, icerik):
                if debug:
                    print(f"  ✅ Rule sonucu kullanıldı: {kategori}")
                return kategori

        return None
    

    def haber_turunu_bul(self, baslik, icerik, debug=False):
        rule_sonuc = self.haber_turunu_bul_rule_based(baslik, icerik, debug=debug)

       
        if rule_sonuc:
            if debug:
                print(f"  ✅ Rule sonucu kullanıldı: {rule_sonuc}")
            return rule_sonuc

       
        semantic_sonuc, semantic_skorlar = self.haber_turunu_bul_semantic(
            baslik, icerik, debug=debug
        )

        if debug:
            print(f"  🤖 Semantic skorlar: {semantic_skorlar}")

        if semantic_sonuc:
            if self._kategori_on_kosulu_saglandi_mi(semantic_sonuc, baslik, icerik):
                if debug:
                    print(f"  ✅ Semantic fallback sonucu kullanıldı: {semantic_sonuc}")
                return semantic_sonuc

        if debug:
            print("  ⛔ Sonuç yok")
        return None

    def _normalize(self, metin):
        return (
            metin.lower()
            .replace("İ", "i").replace("I", "ı")
            .replace("Ğ", "ğ").replace("Ü", "ü")
            .replace("Ş", "ş").replace("Ö", "ö").replace("Ç", "ç")
        )

    def ilce_bul(self, metin):
        
        if not metin:
            return None

        metin_norm = self._normalize(metin)
        eslesenler = []

        for ilce in ILCELER:
            ilce_norm = self._normalize(ilce)
            pattern = r'(?<!\w)' + re.escape(ilce_norm) + r'(?!\w)'
            eslesme = re.search(pattern, metin_norm)
            if eslesme:
                eslesenler.append((ilce, eslesme.start()))

        if not eslesenler:
            return None

        eslesenler.sort(key=lambda x: x[1])
        return eslesenler[0][0]
    

    def kocaeli_ici_mi(self, baslik, icerik):
        metin = f"{baslik} {icerik}"
        metin_norm = self._normalize(metin)

        ilce = self.ilce_bul(metin)
        kocaeli_var = bool(re.search(r'(?<!\w)kocaeli(?!\w)', metin_norm))

        bulunan_diger_sehir = False
        for sehir in DIGER_SEHIRLER:
            pattern = r'(?<!\w)' + re.escape(sehir) + r'(?!\w)'
            if re.search(pattern, metin_norm):
                bulunan_diger_sehir = True
                break

       
        if ilce or kocaeli_var:
            return True

       
        if bulunan_diger_sehir:
            return False

        
        return False

    def konum_bul(self, metin):
        if not metin:
            return "Belirtilmemiş"

        metin_norm = self._normalize(metin)
        ilce_bulunan = self.ilce_bul(metin)
        kocaeli_var = bool(re.search(r'(?<!\w)kocaeli(?!\w)', metin_norm))

       
        for sehir in DIGER_SEHIRLER:
            pattern = r'(?<!\w)' + re.escape(sehir) + r'(?!\w)'
            if re.search(pattern, metin_norm) and not ilce_bulunan and not kocaeli_var:
                return "Belirtilmemiş"

        
        mahalle_eslesmeleri = list(re.finditer(
            r'(?<!\w)([A-ZÇĞİÖŞÜ][a-zA-ZÇĞİÖŞÜçğışöü0-9]+'
            r'(?:\s[A-ZÇĞİÖŞÜ][a-zA-ZÇĞİÖŞÜçğışöü0-9]+){0,2})'
            r'\s+(Mahallesi|Mah\.)',
            metin
        ))

       
        sokak_eslesmeleri = list(re.finditer(
            r'(?<!\w)([A-ZÇĞİÖŞÜ][a-zA-ZÇĞİÖŞÜçğışöü0-9]+'
            r'(?:\s[A-ZÇĞİÖŞÜ][a-zA-ZÇĞİÖŞÜçğışöü0-9]+){0,3}\s+'
            r'(?:Sokak|Sok\.|Caddesi|Cad\.|Bulvarı|Blv\.))',
            metin
        ))

        def ilce_temizle(ad):
            if not ad:
                return ad
            for ilce in ILCELER:
                ad_norm = self._normalize(ad)
                ilce_norm = self._normalize(ilce)
                if ad_norm.startswith(ilce_norm + " "):
                    return ad[len(ilce) + 1:].strip()
            return ad.strip()

        
        if mahalle_eslesmeleri and ilce_bulunan:
            mahalle = ilce_temizle(mahalle_eslesmeleri[0].group(1))
            return f"{mahalle} Mahallesi, {ilce_bulunan}, Kocaeli"

       
        if sokak_eslesmeleri and ilce_bulunan:
            sokak = ilce_temizle(sokak_eslesmeleri[0].group(1))
            return f"{sokak}, {ilce_bulunan}, Kocaeli"

        
        if mahalle_eslesmeleri:
            mahalle = ilce_temizle(mahalle_eslesmeleri[0].group(1))
            return f"{mahalle} Mahallesi, Kocaeli"

       
        yol_eslesmesi = re.search(
            r'\b(TEM|D-100|D-130|D-605|D-650|Kuzey Marmara Otoyolu)\b',
            metin,
            flags=re.IGNORECASE
        )
        if yol_eslesmesi and ilce_bulunan:
            yol_adi = yol_eslesmesi.group(1).upper()
            return f"{yol_adi}, {ilce_bulunan}, Kocaeli"

        
        mekan_eslesmesi = re.search(
            r'((?:[A-ZÇĞİÖŞÜ][a-zA-ZÇĞİÖŞÜçğışöü0-9]+)\s+'
            r'(?:[A-ZÇĞİÖŞÜ][a-zA-ZÇĞİÖŞÜçğışöü0-9]+\s+){0,4}'
            r'(?:Kültür Merkezi|Kongre Merkezi|Merkezi|Merkez|Parkı|Müzesi|Salonu|Stadyumu))',
            metin
        )
        if mekan_eslesmesi and ilce_bulunan:
            mekan = mekan_eslesmesi.group(1).strip()

            gereksiz_baslangiclar = [
                "Hat Sergisi", "Nevbahar", "Sergisi", "Konseri", "Festivali",
                "Tiyatro Oyunu", "Etkinliği"
            ]
            for ifade in gereksiz_baslangiclar:
                if mekan.startswith(ifade + " "):
                    mekan = mekan[len(ifade):].strip()

            for ilce in ILCELER:
                if mekan.startswith(ilce + " "):
                    mekan = mekan[len(ilce):].strip()
                    break

            return f"{mekan}, {ilce_bulunan}, Kocaeli"

        
        if ilce_bulunan:
            return f"{ilce_bulunan}, Kocaeli"

        return "Belirtilmemiş"
    

    def tarih_normalize(self, tarih_metni):
        
        if not tarih_metni or tarih_metni == "Tarih Bulunamadı":
            return None
        iso_match = re.match(r'(\d{4})-(\d{2})-(\d{2})', str(tarih_metni))
        if iso_match:
            return iso_match.group(0)
        tr_match = re.match(
            r'(\d{1,2})\s+(Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|'
            r'Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık)\s+(\d{4})',
            str(tarih_metni).strip()
        )
        if tr_match:
            gun = tr_match.group(1).zfill(2)
            ay = AYLAR.get(tr_match.group(2), "01")
            yil = tr_match.group(3)
            return f"{yil}-{ay}-{gun}"
        dot_match = re.match(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', str(tarih_metni).strip())
        if dot_match:
            gun = dot_match.group(1).zfill(2)
            ay = dot_match.group(2).zfill(2)
            yil = dot_match.group(3)
            return f"{yil}-{ay}-{gun}"
        return None

    def haber_yeni_mi(self, tarih_metni):
        if not tarih_metni or tarih_metni == "Tarih Bulunamadı":
            return True
        try:
            tarih_iso = self.tarih_normalize(tarih_metni)
            if not tarih_iso:
                return True
            tarih_obj = datetime.strptime(tarih_iso, "%Y-%m-%d")
            fark = datetime.now() - tarih_obj
            return fark.days <= 3
        except Exception:
            return True

    def tarih_cikart(self, soup, html):
        for script in soup.find_all("script", type="application/ld+json"):
            if script.string:
                try:
                    veri = json.loads(script.string)
                    if isinstance(veri, dict) and "datePublished" in veri:
                        return veri["datePublished"]
                    if isinstance(veri, list):
                        for item in veri:
                            if isinstance(item, dict) and "datePublished" in item:
                                return item["datePublished"]
                except Exception:
                    pass

        zaman = soup.find("time")
        if zaman and zaman.has_attr("datetime"):
            return zaman["datetime"]

        for meta_name in ["article:published_time", "datePublished", "publish_date"]:
            meta = soup.find("meta", attrs={"property": meta_name}) or \
                   soup.find("meta", attrs={"name": meta_name})
            if meta and meta.get("content"):
                return meta["content"]

        eslesme = re.search(
            r"(\d{1,2})\s+(Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|"
            r"Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık)\s+(\d{4})",
            html
        )
        if eslesme:
            return eslesme.group(0)

        eslesme2 = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", html)
        if eslesme2:
            return eslesme2.group(0)

        return "Tarih Bulunamadı"

    def veritabanina_kaydet(self, haber):
        
        if not haber.get("haber_turu") or haber["haber_turu"] == "Diğer":
            return False
        
        baslik = haber.get("haber_basligi", "")
        icerik = haber.get("haber_icerigi", "")

        if not self.kocaeli_ici_mi(baslik, icerik):
            return False

        if haberler_col.find_one({"haber_linki": haber["haber_linki"]}):
            return False

        
        tarih_raw = haber.get("yayin_tarihi")
        tarih_iso = self.tarih_normalize(tarih_raw)
        if tarih_iso:
            haber["yayin_tarihi"] = tarih_iso

    
        konum = haber.get("konum_metni", "")
        baslik = haber.get("haber_basligi", "")
        icerik = haber.get("haber_icerigi", "")
        ilce = self.ilce_bul(konum) or self.ilce_bul(baslik + " " + icerik)
        haber["ilce"] = ilce

        if "ek_linkler" not in haber:
            haber["ek_linkler"] = []

        haberler_col.insert_one(haber)
        tarih = haber.get("yayin_tarihi", "")[:10] if haber.get("yayin_tarihi") else "?"
        baslik_kisa = haber.get("haber_basligi", "")[:40]
        print(f"  ✅ Kaydedildi ({tarih}): {baslik_kisa}...")
        return True

    def scrape(self):
        raise NotImplementedError("Her scraper kendi scrape() metodunu yazmalı.")







