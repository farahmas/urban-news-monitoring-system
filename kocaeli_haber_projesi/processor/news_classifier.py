import numpy as np

ONCELIK_SIRASI = [
    "Trafik Kazası",
    "Yangın",
    "Elektrik Kesintisi",
    "Hırsızlık",
    "Kültürel Etkinlikler",
]

KATEGORI_ORNEKLERI = {
    "Trafik Kazası": [
        "İki aracın çarpıştığı trafik kazasında yaralananlar hastaneye kaldırıldı.",
        "TEM otoyolunda zincirleme kaza meydana geldi.",
        "Direksiyon hakimiyetini kaybeden sürücü bariyerlere çarptı.",
        "Motosiklet ile otomobilin çarpıştığı kazada bir kişi yaralandı.",
        "D-100 karayolunda meydana gelen kazada trafik durdu.",
        "TIR devrildi, yol ulaşıma kapandı.",
        "Şarampole yuvarlanan araçta yaralılar var.",
        "Kavşakta meydana gelen feci kazada can kaybı yaşandı.",
        "Kamyondan düşen tomruk otomobile saplandı, sürücü yaralandı.",
        "TEM'de zincirleme kazada araçlar birbirine girdi.",
        "Kontrolden çıkan otomobil bariyerlere çarptı.",
        "Yola dökülen atıklar nedeniyle zincirleme trafik kazası meydana geldi.",
    ],
    "Yangın": [
        "Evde çıkan yangına itfaiye ekipleri müdahale etti.",
        "Fabrikada çıkan yangın kontrol altına alındı.",
        "Araç alev aldı, sürücü son anda kurtuldu.",
        "Çatı yangını mahallede paniğe neden oldu.",
        "Otluk alanda çıkan yangın büyümeden söndürüldü.",
        "Depoda çıkan yangın sonrası soğutma çalışması yapıldı.",
        "Bacada çıkan yangın itfaiyenin müdahalesiyle söndürüldü.",
        "Orman yangını ekiplerin yoğun çalışmasıyla kontrol altına alındı.",
        "Şofben alev aldı, evde panik yaşandı.",
        "Yangına itfaiye ekipleri müdahale etti.",
        "Çıkan yangın kısa sürede kontrol altına alındı.",
        "Soba yangını sonrası evde facia yaşandı.",
    ],
    "Elektrik Kesintisi": [
        "SEDAŞ planlı elektrik kesintisi programını açıkladı.",
        "İlçede bakım çalışması nedeniyle elektrik verilemeyecek.",
        "Mahalleler saatlerce elektriksiz kalacak.",
        "Trafo arızası nedeniyle enerji kesintisi yaşanacak.",
        "Planlı kesinti nedeniyle bazı bölgelerde elektrik olmayacak.",
        "Şebeke arızası yüzünden elektrik kesintisi uygulanacak.",
        "Elektrikler kesilecek, vatandaşlara uyarı yapıldı.",
        "Kesintiden etkilenecek mahalleler açıklandı.",
    ],
    "Hırsızlık": [
        "Hırsızlık şüphelisi polis ekipleri tarafından yakalandı.",
        "Ev soyuldu, çalınan eşyalar aranıyor.",
        "Kablo hırsızlığı yapan zanlılar tutuklandı.",
        "Çalıntı motosikletle yakalanan şüpheli gözaltına alındı.",
        "İş yerinden para çalan kişi güvenlik kameralarına yakalandı.",
        "Kapkaç olayı sonrası polis çalışma başlattı.",
        "Aracın çalındığı ihbarı üzerine ekipler harekete geçti.",
        "Kuyumcu soygununa karışan zanlı tutuklandı.",
        "Kablo hırsızlığı yapan zanlılar yakalandı.",
        "Çalıntı motosikletle yakalanan şüpheli gözaltına alındı.",
        "Ev soyuldu, ziynet eşyaları çalındı.",
        "Hırsızlık suçundan aranan şahıs tutuklandı.",
    ],
    "Kültürel Etkinlikler": [
        "Kültür merkezinde konser düzenlendi.",
        "Sergi ziyarete açıldı.",
        "Tiyatro oyunu sanatseverlerle buluştu.",
        "Festival kapsamında çeşitli etkinlikler düzenlendi.",
        "Söyleşi programı yoğun katılımla gerçekleştirildi.",
        "Müzik dinletisi izleyicilerden büyük beğeni topladı.",
        "Kitap fuarı kapılarını ziyaretçilere açtı.",
        "Hat sergisi kültür merkezinde ziyarete açıldı.",
        "Kütüphane haftası etkinlikleri kapsamında çocuklar bir araya geldi.",
        "Kültür merkezinde tiyatro gösterisi düzenlendi.",
        "Festival ve sergi programı yoğun katılımla gerçekleşti.",
        "Türk Müziği gecesi sanatseverleri büyüledi.",
    ],
}

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

_MODEL = None
_KATEGORI_VEKTORLERI = None

def get_model():
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return _MODEL

def get_kategori_vektorleri():
    global _KATEGORI_VEKTORLERI
    if _KATEGORI_VEKTORLERI is None:
        model = get_model()
        _KATEGORI_VEKTORLERI = {}
        for kategori, ornekler in KATEGORI_ORNEKLERI.items():
            emb = model.encode(ornekler, convert_to_numpy=True)
            _KATEGORI_VEKTORLERI[kategori] = emb.mean(axis=0)
    return _KATEGORI_VEKTORLERI

def semantic_kategori_skorlari(metin):
    model = get_model()
    kategori_vektorleri = get_kategori_vektorleri()

    haber_emb = model.encode(metin, convert_to_numpy=True).reshape(1, -1)

    skorlar = {}
    for kategori, vektor in kategori_vektorleri.items():
        skor = cosine_similarity(haber_emb, vektor.reshape(1, -1))[0][0]
        skorlar[kategori] = float(skor)

    return skorlar

