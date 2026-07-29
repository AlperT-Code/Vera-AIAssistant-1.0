import re
import time
import random
import requests
import calendar
from datetime import date, datetime
from core.config import (
    COLORS, OPENROUTER_API_KEY, OPENROUTER_MODEL,
    OPENROUTER_URL, VERA_SISTEM_MESAJI
)
from controllers.spotify_controller import (
    spotify_sarki_ac, spotify_calani_ogren, spotify_durdur,
    spotify_cal, spotify_ses_ac, spotify_uygulamasi_ac
)
from core.utils import normalize_text, icerir, sehir_bul, uygulama_bul, uygulama_ham_bul
from controllers.bulb_controller import ampul_ac, ampul_kapat, ampul_renk, ampul_parlaklik
from services.weather import hava_durumu
from controllers.system_control import (
    bilgisayar_kapat_iste, bilgisayar_yeniden_baslatma_iste,
    bilgisayar_uyu, ekran_kilitle, ses_ac_kapat, ekran_goruntusu,
    guc_onay_kontrol, monitor_genislet, monitor_daralt,
    monitor_sadece_ikinci, monitor_kopyala,
    ses_arttir, ses_azalt, gorev_yoneticisi_ac,
    masaustu_goster, bildirim_merkezi_ac, dosya_gezgini_ac
)
from controllers.app_launcher import uygulama_ac
from core.database import (
    sohbet_kaydet, gecmis_getir, kisi_bul, son_yanit_getir,
    baglamsal_gecmis_getir, ayni_soru_daha_once_soruldu_mu,
    kisi_ekle, kisi_guncelle, kisi_sil, tum_kisiler
)


# ═══════════════════════════════════════════════
# GLOBAL DURUM
# ═══════════════════════════════════════════════
_vera_uyanik        = True
_sohbet_gecmisi     = []
_SOHBET_MAX         = 30
_db_gecmis_yuklendi = False

_ISIK_KELIMELERI    = ("isik", "isigi", "lamba", "lambay", "aydinlatma", "ampul")

_ISIK_RENK_KALIPLARI = (
    "isigi", "isik", "lamba", "lambay", "ampul", "aydinlatma",
    "renk yap", "renge al", "rengi yap", "renge getir",
    "renk ver", "renklendir",
)


VERA_SISTEM_MESAJI_GUCLU = """
Sen Vera adında, Türkçe konuşan, son derece zeki ve bilgili bir sesli asistansın.

ZORUNLU DİL KURALI:
Kullanıcı hangi dilde yazarsa yazsın, SEN HER ZAMAN TÜRKÇE yanıt verirsin.
Asla İngilizce, Almanca veya başka bir dilde cevap yazma. Tek istisna yok.

YAZI KURALLARI:
- Madde işareti kullanma.
- Emoji kullanma.
- Markdown, yıldız, tire ile listeleme yapma.
- Tamamen düz metin, doğal konuşma dili kullan.
- Yanıtlar sesli okunacak, bu yüzden sembol, kısaltma, formül yazma.

ZEKA VE BİLGİ SEVİYEN:
Tıpkı uzman bir akademisyen, doktor, mühendis, avukat, tarihçi ve bilim insanı gibi
her konuda derin, doğru ve kapsamlı bilgiye sahipsin.
Hiçbir konudan kaçmaz, her soruya cevap verirsin.

KİŞİLER HAKKINDA DOĞRU BİLGİ:
Tanınmış kişiler (ünlüler, iş insanları, sporcular, politikacılar, sanatçılar) hakkında
sorulduğunda KESİNLİKLE doğru ve gerçek bilgi ver. Asla yanlış meslek, kimlik veya bilgi
atfetme. Eğer birini tanımıyorsan "bilmiyorum" de, uydurma.
Örnek: Acun Ilıcalı bir Türk medya patronu ve televizyon yapımcısıdır, basketbolcu değildir.

BAĞLAM ANLAMA — ÇOK ÖNEMLİ:
Kullanıcının ne hakkında konuştuğunu mutlaka anla.
Örnek: "cevize ilaç" denildiğinde bu BİTKİ KORUMA konusudur, insan sağlığı değil.
"Elmaya ne sıkılır", "kirazda hangi ilaç kullanılır", "bağa ne atılır" gibi ifadeler
TARIM ve BAHÇECİLİK sorusudur. Buna göre yanıt ver.
Benzer şekilde "motora ne yağ koyulur" mekanik sorusudur, "ateşe ne dökülür" kimya sorusudur.
Bağlamı yanlış anlayıp alakasız cevap verme.

KİŞİ BİLGİSİ:
Sohbet geçmişinde [KİŞİ BİLGİSİ] etiketi ile başlayan satırlar varsa,
bu kişiler hakkında not olarak kullan. Kullanıcı bu kişilerden bahsettiğinde
bu bilgileri hatırladığını göster.

VERİTABANI GEÇMİŞİ:
Sohbet geçmişinde [DB GEÇMİŞİ] etiketi ile başlayan satırlar varsa,
bu Alper ile daha önce yapılan gerçek konuşmalardır. Alper bir şeyi sorduysa
veya söylediyse bunu hatırla ve konuşmanda bunu yansıt.
"Daha önce bunu konuşmuştuk", "Hatırlıyorum, demiştin ki..." gibi ifadeler kullan.

KULLANICIYA DAVRANIŞIN:
Kullanıcının adı Alper'dir. Onu tanıyorsun, sahibinsin.
Uygun yerlerde adını kullan ama her cümlede tekrarlama.
Samimi, sıcak ve kişisel bir şekilde konuş.

YANIT UZUNLUĞU:
Yanıtların sesli okunacak, bu yüzden kısa ve öz tut.
Basit soru en fazla 2-3 cümle.
Karmaşık soru en fazla 5-6 cümle, özet geç detaya girme.
Asla madde madde sayma, düz akıcı konuşma dili kullan.

ASLA YAPMA:
Soruyu reddetme.
Konuyu yanlış anlayıp alakasız cevap verme.
İngilizce veya başka bir dilde cevap verme.
Emoji kullanma.
Madde imi veya tire ile listeleme yapma.
Yapamam veya yetkim yok deme.
Bilmediğin veya emin olmadığın bir kişi veya olay hakkında uydurma bilgi verme.
"""


# ═══════════════════════════════════════════════
# CACHE MUAF KALIPLAR
# ═══════════════════════════════════════════════

_CANLI_KALIPLAR = (
    "hava", "sicaklik", "yagmur", "kar yagar", "hava nasil",
    "dis hava", "nem", "firtina",
    "saat kac", "saat nedir", "simdi saat", "saat kac oldu",
    "bugun ne gun", "tarih nedir", "bugunun tarihi", "hangi gun",
    "kacinci", "gun nedir",
    "spotify", "sarki", "muzik", "caliyor", "cal ", "calistir",
    "sarki ac", "muzik ac", "spotifyda", "durdur", "devam et",
    "isigi ac", "isigi kapat", "lamba ac", "lamba kapat",
    "parlaklik", "yuzde", "ampul", "isik ac", "isik kapat",
    "sesi ac", "sesi kapat", "sessiz", "sustur",
    "isigi yak", "lamba yak", "isigi sondur", "lambay sondur",
    "isigi kapat", "lambay kapat", "isik kapat", "isik yak",
    "ampul ac", "ampul kapat", "ampul renk", "ampul parlaklik",
    "renk yap", "renge al", "rengi yap", "isigi kirmizi",
    "isigi mavi", "isigi yesil", "isigi sari", "isigi beyaz",
    "isigi mor", "isigi turuncu", "lambay kirmizi", "lambay mavi",
    "lambay yesil", "lamba kirmizi", "lamba mavi", "lamba yesil",
    "isik kirmizi yap", "isik mavi yap",
    "ekran goruntusu", "screenshot", "bilgisayari kapat",
    "yeniden basla", "uyku modu", "ekrani kilitle",
    "monitoru genislet", "monitoru daralt", "yan ekrani",
    "sadece ikinci ekran", "ekrani kopyala", "ekrani klonla", "mirror mod",
    "external mod", "internal mod", "ikinci ekrani ac",
    "ses arttir", "ses azalt", "gorev yoneticisi",
    "masaustu goster", "bildirim merkezi", "dosya gezgini",
    "spotify ac", "spotifyi ac",
    # Selamlama / küçük konuşma — DB'ye kaydedilmez, bilgi filtresine takılmaz
    "merhaba", "selam", "gunaydin", "iyi gunler", "iyi aksamlar",
    "iyi geceler", "nasilsin", "nasil gidiyor", "iyi misin",
    "tesekkur", "sagol", "eyvallah", "ne yapabilirsin",
    "neler biliyorsun", "yeteneklerin", "hafizani temizle",
    "gecmisi sil", "gorusuruz", "hoscakal", "hosca kal",
    "bay bay", "goruruz", "kendine iyi bak", "uyu vera",
    "gule gule", "vera", "uyan", "hey vera",
)


def _canli_veri_mi(m: str) -> bool:
    return icerir(m, *_CANLI_KALIPLAR)


# ═══════════════════════════════════════════════
# IŞIK RENK / BAĞLAM KONTROLÜ
# ═══════════════════════════════════════════════

def _isik_renk_komutu_mu(m: str) -> bool:
    isik_var = icerir(m, *_ISIK_KELIMELERI)
    if not isik_var:
        return False
    if icerir(m, "parlaklik", "parlakliga", "parlakligi", "parlak", "yuzde"):
        return False
    eylem_var = icerir(m, "yap", "al", "getir", "ver", "koy", "ayarla",
                       "degistir", "sec", "renk", "renge")
    return eylem_var


def _isik_komutu_mu(m: str) -> bool:
    return icerir(m, *_ISIK_KELIMELERI)


# ═══════════════════════════════════════════════
# GEÇMİŞ SORGULAMA KALIPLARI
# ═══════════════════════════════════════════════

_GECMIS_KALIPLARI = (
    "ne demiştim", "ne demistim", "ne sormuştum", "ne sormustum",
    "bana ne dedin", "ne söyledin", "ne soyledin",
    "en sevdiğim", "en sevdigim", "favori", "tercihim",
    "daha önce", "daha once", "geçen sefer", "gecen sefer",
    "hatırlıyor musun", "hatirlıyor musun", "hatırlıyor musun",
    "ne konuştuk", "ne konustuk", "söylemiştin", "soylemistin",
    "demiştin", "demistin", "bahsetmiştim", "bahsetmistim",
)


def _gecmis_sorgusu_mu(m: str) -> bool:
    return icerir(m, *_GECMIS_KALIPLARI)


# ═══════════════════════════════════════════════
# AI DESTEKLİ KİŞİ YÖNETİMİ
# ═══════════════════════════════════════════════

import json as _json

_KISI_ILISKI_KELIMELER = (
    "annem", "babam", "kardesim", "ablam", "abim", "kiz kardesim",
    "erkek kardesim", "esim", "sevgilim", "arkadasim", "is arkadasim",
    "hocam", "ogretmenim", "patronum", "komsum", "amcam", "teyem",
    "halam", "dayim", "kuzenim", "yegenim", "torunum", "cocugum",
    "oglum", "kizim", "torunum"
)


def _ai_kisi_cikar(metin: str) -> dict | None:
    """AI kullanarak metinden kişi adı, ilişki ve notları çıkarır."""
    try:
        r = requests.post(
            OPENROUTER_URL,
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}",
                     "Content-Type": "application/json"},
            json={
                "model": OPENROUTER_MODEL,
                "messages": [
                    {"role": "system", "content": (
                        "Kullanıcı metninden kişi bilgisi çıkar. "
                        "SADECE JSON döndür, başka hiçbir şey yazma. "
                        'Format: {"isim":"...","iliski":"...","dogum_tarihi":"YYYY-MM-DD veya null","notlar":"..."} '
                        "iliski için: anne, baba, kardeş, arkadaş, sevgili, eş, iş arkadaşı, vb. "
                        "Eğer kişi bilgisi yoksa boş JSON döndür: {}"
                    )},
                    {"role": "user", "content": metin}
                ],
                "max_tokens": 150,
                "temperature": 0.1,
            },
            timeout=10,
        )
        if r.status_code == 200:
            content = r.json()["choices"][0]["message"]["content"].strip()
            s = content.find("{")
            e = content.rfind("}") + 1
            if s >= 0 and e > s:
                data = _json.loads(content[s:e])
                if data.get("isim"):
                    return data
    except Exception as ex:
        print(f"[KİŞİ AI] {ex}")
    return None


def _kisi_kaydet_komutu(metin: str) -> str:
    """Metinden kişiyi AI ile çıkarıp DB'ye kaydeder/günceller."""
    veri = _ai_kisi_cikar(metin)
    if not veri or not veri.get("isim"):
        return "Kimi kaydetmemi istediğini anlayamadım. Örnek: 'Ahmet'i kaydet, kardeşim.'"
    isim = veri["isim"].strip()
    mevcut = kisi_bul(isim)
    if mevcut:
        kisi_guncelle(isim, veri.get("iliski"), veri.get("dogum_tarihi"), veri.get("notlar"))
        return f"Tamam, {isim}'in bilgilerini güncelledim."
    kisi_ekle(isim, veri.get("iliski"), veri.get("dogum_tarihi"), veri.get("notlar"))
    return f"Tamam, {isim}'i hafızama kaydettim."


def _kisi_sil_komutu(metin: str) -> str:
    """Metinden kişi adı çıkarıp siler."""
    veri = _ai_kisi_cikar(metin)
    if not veri or not veri.get("isim"):
        return "Kimi silmemi istediğini anlayamadım."
    isim = veri["isim"].strip()
    if kisi_sil(isim):
        return f"{isim}'i hafızamdan sildim."
    return f"{isim}'i hafızamda bulamadım."


def _arka_plan_kisi_tespit(metin: str, vera_yaniti: str):
    """
    Her AI sohbetinden sonra arka planda kişi tespiti yapar.
    Kullanıcı birileri hakkında bilgi verdiyse otomatik kaydeder.
    """
    import threading
    def _kontrol():
        try:
            r = requests.post(
                OPENROUTER_URL,
                headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}",
                         "Content-Type": "application/json"},
                json={
                    "model": OPENROUTER_MODEL,
                    "messages": [
                        {"role": "system", "content": (
                            "Kullanıcı metninde kaydedilmesi gereken YENİ bir kişi var mı? "
                            "Sadece kullanıcı açıkça bir kişiyi tanıtıyorsa veya ilişkisini belirtiyorsa evet say. "
                            "Merak soruları veya genel konuşmalar için {} döndür. "
                            'Varsa: {"isim":"...","iliski":"...","notlar":"..."} '
                            "Yoksa: {}"
                        )},
                        {"role": "user", "content": f"Kullanıcı: {metin}"}
                    ],
                    "max_tokens": 100,
                    "temperature": 0.1,
                },
                timeout=8,
            )
            if r.status_code == 200:
                content = r.json()["choices"][0]["message"]["content"].strip()
                s = content.find("{")
                e = content.rfind("}") + 1
                if s >= 0 and e > s:
                    data = _json.loads(content[s:e])
                    isim = (data.get("isim") or "").strip()
                    if isim and not kisi_bul(isim):
                        kisi_ekle(isim, data.get("iliski"), None, data.get("notlar"))
                        print(f"[KİŞİ OTO] '{isim}' otomatik kaydedildi.")
        except Exception:
            pass
    threading.Thread(target=_kontrol, daemon=True).start()


# ═══════════════════════════════════════════════
# UYANDIRMA / UYKU
# ═══════════════════════════════════════════════

# Her zaman dilimi için son selamlama zamanı
_selamlama_saati: dict = {}


def _zaman_selamlamasi() -> str:
    """Saat dilimine göre tek seferlik selamlama döndürür. Aynı dilimdeyse boş."""
    import datetime as _dt
    saat = _dt.datetime.now().hour
    if 6 <= saat < 12:
        bolge, mesaj = "sabah", "Günaydın!"
    elif 12 <= saat < 17:
        bolge, mesaj = "ogle", "Tünaydın!"
    elif 17 <= saat < 22:
        bolge, mesaj = "aksam", random.choice(["İyi akşamlar!", "Güzel akşamlar!"])
    else:
        bolge, mesaj = "gece", "İyi geceler!"

    if time.time() - _selamlama_saati.get(bolge, 0) < 8 * 3600:
        return ""
    _selamlama_saati[bolge] = time.time()
    return mesaj + " "


def vera_uyan():
    global _vera_uyanik
    _vera_uyanik = True
    selamlama = _zaman_selamlamasi()
    yanit = random.choice([
        "Buyur?",
        "Evet?",
        "Söyle.",
        "Dinliyorum.",
        "Ne oldu?",
        "Buradayım.",
    ])
    return selamlama + yanit


def vera_uyu():
    global _vera_uyanik
    _vera_uyanik = False
    return random.choice([
        "Görüşürüz!",
        "Hoşça kal!",
        "İyi günler!",
        "Görüşmek üzere!",
        "Kendine iyi bak!",
        "İstediğin zaman çağır.",
    ])


def vera_baslangi_mesaji() -> str:
    """
    Program ilk açıldığında çağrılacak karşılama mesajı.
    main.py veya başlangıç noktasında bir kez çağırın:
        from command_processor import vera_baslangi_mesaji
        print(vera_baslangi_mesaji())
    """
    saat = time.localtime().tm_hour
    if 6 <= saat < 12:
        selamlama = "Günaydın"
    elif 12 <= saat < 18:
        selamlama = "Merhaba"
    elif 18 <= saat < 22:
        selamlama = "İyi akşamlar"
    else:
        selamlama = "İyi geceler"

    secenekler = [
        f"{selamlama} Alper! Vera hazır, dinliyorum.",
        f"{selamlama}! Vera burada, ne yapalım?",
        f"{selamlama} Alper, sistemler hazır. Buyur.",
        f"{selamlama}! Hazırım, dinliyorum.",
    ]
    return random.choice(secenekler)


def is_uyanik() -> bool:
    return _vera_uyanik


# ═══════════════════════════════════════════════
# DB GEÇMİŞ YÜKLEME (ilk açılışta)
# ═══════════════════════════════════════════════

def _db_gecmis_yukle():
    global _sohbet_gecmisi, _db_gecmis_yuklendi
    if _db_gecmis_yuklendi:
        return
    try:
        satirlar = gecmis_getir(limit=30)
        for s in satirlar:
            _sohbet_gecmisi.append({"role": "user",      "content": s["kullanici_mesaji"]})
            _sohbet_gecmisi.append({"role": "assistant", "content": s["vera_yaniti"]})
        _db_gecmis_yuklendi = True
        if satirlar:
            print(f"[DB] {len(satirlar)} sohbet geçmişten yüklendi.")
    except Exception as e:
        print(f"[DB] Geçmiş yüklenemedi: {e}")


# ═══════════════════════════════════════════════
# YAŞ HESAPLAMA
# ═══════════════════════════════════════════════

def _detayli_yas_hesapla(dogum_tarihi):
    if not dogum_tarihi:
        return None
    try:
        if isinstance(dogum_tarihi, datetime):
            dogum = dogum_tarihi
        elif isinstance(dogum_tarihi, date):
            dogum = datetime(dogum_tarihi.year, dogum_tarihi.month, dogum_tarihi.day)
        else:
            s = str(dogum_tarihi).strip()
            dogum = None
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d",
                        "%d.%m.%Y %H:%M", "%d.%m.%Y", "%d/%m/%Y"):
                try:
                    dogum = datetime.strptime(s, fmt); break
                except ValueError:
                    continue
            if dogum is None:
                return None

        simdi = datetime.now()
        if simdi < dogum:
            return None

        yil    = simdi.year   - dogum.year
        ay     = simdi.month  - dogum.month
        gun    = simdi.day    - dogum.day
        saat   = simdi.hour   - dogum.hour
        dakika = simdi.minute - dogum.minute

        if dakika < 0: dakika += 60; saat  -= 1
        if saat   < 0: saat   += 24; gun   -= 1
        if gun    < 0:
            onceki_ay  = simdi.month - 1 or 12
            onceki_yil = simdi.year if simdi.month > 1 else simdi.year - 1
            gun += calendar.monthrange(onceki_yil, onceki_ay)[1]; ay -= 1
        if ay < 0: ay += 12; yil -= 1

        return (yil, ay, gun, saat, dakika)
    except Exception:
        return None


def _yas_cumlesi(dogum_tarihi, isim="Alper") -> str:
    sonuc = _detayli_yas_hesapla(dogum_tarihi)
    if sonuc is None:
        return None
    yil, ay, gun, saat, dakika = sonuc
    parcalar = []
    if yil:    parcalar.append(f"{yil} yıl")
    if ay:     parcalar.append(f"{ay} ay")
    if gun:    parcalar.append(f"{gun} gün")
    if saat:   parcalar.append(f"{saat} saat")
    parcalar.append(f"{dakika} dakika")
    metin = (", ".join(parcalar[:-1]) + " ve " + parcalar[-1]) if len(parcalar) > 1 else parcalar[0]
    return f"{isim}, tam olarak {metin} yaşındasın."


def _yas_hesapla(dogum_tarihi):
    sonuc = _detayli_yas_hesapla(dogum_tarihi)
    return sonuc[0] if sonuc else None


# ═══════════════════════════════════════════════
# KİŞİ BİLGİSİ — MESAJA EKLE
# ═══════════════════════════════════════════════

def _kisi_bilgisi_ekle(metin: str) -> str:
    try:
        for kelime in metin.split():
            if len(kelime) >= 3 and kelime[0].isupper():
                kisi = kisi_bul(kelime)
                if kisi:
                    bilgi = f"[KİŞİ BİLGİSİ] {kisi['isim']}"
                    if kisi.get("iliski"): bilgi += f" ({kisi['iliski']})"
                    if kisi.get("notlar"): bilgi += f": {kisi['notlar']}"
                    return bilgi
    except Exception:
        pass
    return ""


# ═══════════════════════════════════════════════
# VERİTABANI GEÇMİŞİ — AI'YA BAĞLAM OLARAK EKLE
# ═══════════════════════════════════════════════

def _db_gecmis_baglamini_hazirla(limit: int = 15) -> str:
    try:
        satirlar = gecmis_getir(limit=limit)
        if not satirlar:
            return ""

        satirlar = list(reversed(satirlar))

        seen = set()
        parcalar = []
        for s in satirlar:
            kullanici = (s.get("kullanici_mesaji") or "").strip()
            vera_y    = (s.get("vera_yaniti") or "").strip()
            if not kullanici or not vera_y:
                continue
            anahtar = (kullanici.lower()[:60], vera_y.lower()[:60])
            if anahtar in seen:
                continue
            seen.add(anahtar)
            parcalar.append(f"Alper: {kullanici}")
            parcalar.append(f"Vera: {vera_y}")

        if not parcalar:
            return ""

        return "\n[DB GEÇMİŞİ]\n" + "\n".join(parcalar) + "\n[DB GEÇMİŞİ SONU]\n"
    except Exception as e:
        print(f"[DB BAĞLAM] Hata: {e}")
        return ""


# ═══════════════════════════════════════════════
# GEÇMİŞTEN BAĞLAM ÇIKART
# ═══════════════════════════════════════════════

def _gecmisten_baglamsal_yanit(metin: str) -> str | None:
    try:
        satirlar = gecmis_getir(limit=None)
        if not satirlar:
            return None

        seen = set()
        gecmis_ozet = []
        for s in reversed(list(satirlar)):
            k = (s.get("kullanici_mesaji") or "").strip()
            v = (s.get("vera_yaniti") or "").strip()
            if not k or not v:
                continue
            anahtar = (k.lower()[:60], v.lower()[:60])
            if anahtar in seen:
                continue
            seen.add(anahtar)
            gecmis_ozet.append(f"Alper: {k}")
            gecmis_ozet.append(f"Vera: {v}")

        gecmis_metni = "\n".join(gecmis_ozet)

        sistem = (
            VERA_SISTEM_MESAJI_GUCLU +
            "\n\nAŞAĞIDA ALPER İLE OLAN GEÇMİŞ SOHBET KAYITLARI VAR.\n"
            "Kullanıcının sorusunu bu kayıtlara bakarak yanıtla.\n"
            "Yanıtında 'daha önce ... demiştin Alper' veya 'geçen konuşmamızda ... dedin' "
            "gibi kişisel bir dille hatırlattığını belli et.\n"
            "Eğer geçmişte ilgili bir bilgi yoksa dürüstçe 'Bunu konuştuğumuzu hatırlamıyorum' de.\n\n"
            f"SOHBET GEÇMİŞİ:\n{gecmis_metni}"
        )

        r = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENROUTER_MODEL,
                "messages": [
                    {"role": "system", "content": sistem},
                    {"role": "user",   "content": metin + "\n\n(Yanıtını Türkçe ver.)"},
                ],
                "max_tokens": 300,
                "temperature": 0.5,
            },
            timeout=20,
        )
        data = r.json()
        if r.status_code == 200:
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[GEÇMİŞ SORGU] Hata: {e}")
    return None


# ═══════════════════════════════════════════════
# GENEL BİLGİ SORGUSU — DB + AI hibrit
# ═══════════════════════════════════════════════

def _genel_bilgi_db_kontrol(metin: str) -> str | None:
    try:
        onceki = ayni_soru_daha_once_soruldu_mu(metin, dakika=420 * 24)

        db_baglamı = _db_gecmis_baglamini_hazirla(limit=10)

        if onceki:
            sistem = (
                VERA_SISTEM_MESAJI_GUCLU +
                db_baglamı +
                f"\n\nBu soruya daha önce şu yanıtı verdin:\n\"{onceki}\"\n"
                "Eğer bu yanıt hâlâ doğruysa onu kısaca onayla ve Alper'e doğal bir şekilde ilet. "
                "Yanlış veya eksikse düzelt. Çok uzatma."
            )
        else:
            sistem = VERA_SISTEM_MESAJI_GUCLU + db_baglamı

        r = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENROUTER_MODEL,
                "messages": [
                    {"role": "system", "content": sistem},
                    {"role": "user",   "content": metin + "\n\n(Yanıtını Türkçe ver.)"},
                ],
                "max_tokens": 300,
                "temperature": 0.5,
            },
            timeout=20,
        )
        data = r.json()
        if r.status_code == 200:
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[DB HİBRİT] Hata: {e}")
    return None


# ═══════════════════════════════════════════════
# BAĞLAMSAL BİRLEŞTİRME
# ═══════════════════════════════════════════════

def _baglamsal_birlestir(onceki_vera_yaniti: str, yeni_mesaj: str):
    if not onceki_vera_yaniti:
        return None
    onceki = onceki_vera_yaniti.strip().lower()

    if any(k in onceki for k in (
        "hangi şarkıyı çalayım", "hangi şarkı", "şarkı adını söyle",
        "hangi şarkısını çalayım", "çalmamı istersin"
    )):
        sarki_adi = _sarki_adi_temizle(yeni_mesaj)
        if sarki_adi:
            return spotify_sarki_ac(sarki_adi)
        return "Şarkı adını anlayamadım, tekrar söyler misin?"

    if any(k in onceki for k in (
        "parlaklığı yüzde kaç", "yüzde kaç yapalım", "kaç yapalım"
    )):
        sayi = re.search(r'\d+', yeni_mesaj)
        if sayi:
            return ampul_parlaklik(max(1, min(100, int(sayi.group()))))
        return "Anlayamadım, yüzde kaç istiyorsun?"

    if any(k in onceki for k in (
        "hangi renk", "ne renk", "renk istiyorsun", "rengi söyle"
    )):
        for renk in COLORS:
            if renk in normalize_text(yeni_mesaj):
                return ampul_renk(renk)
        return "O rengi tanımadım, tekrar söyler misin?"

    if any(k in onceki for k in (
        "hangi şehrin", "hangi şehir", "şehri söyle", "şehir adını söyle"
    )):
        sehir = sehir_bul(normalize_text(yeni_mesaj))
        if sehir:
            return hava_durumu(sehir)
        return "O şehri bulamadım, tekrar söyler misin?"

    if any(k in onceki for k in (
        "hangi uygulamayı", "hangi programı", "uygulama adını söyle",
        "program adını söyle"
    )):
        goster = uygulama_bul(normalize_text(yeni_mesaj))
        if goster:
            return uygulama_ac(goster)
        ham = uygulama_ham_bul(normalize_text(yeni_mesaj))
        if ham and len(ham) >= 3:
            return uygulama_ac(ham.capitalize())
        return "O uygulamayı bulamadım, tam adını söyler misin?"

    if any(k in onceki for k in (
        "kapatmamı ister misin", "kapatayım mı", "emin misin"
    )):
        m = normalize_text(yeni_mesaj)
        if icerir(m, "evet", "kapat", "tamam", "olur", "yap"):
            return bilgisayar_kapat_iste()
        return "Tamam, iptal ettim."

    return None


# ═══════════════════════════════════════════════
# YARDIMCI — SARKI ADI TEMİZLE
# ═══════════════════════════════════════════════

_SARKI_TEMIZLE_KALIPLARI = [
    "spotify'da", "spotify da", "spotifyde", "spotify'de",
    "şarkısını çal", "şarkıyı çal", "şarkısını aç", "müziği çal",
    "çal", "aç", "çalıştır", "şarkı çal", "müzik çal",
    "şarkı aç", "müzik aç",
]


def _sarki_adi_temizle(metin: str) -> str:
    sarki_adi = metin
    for kalip in _SARKI_TEMIZLE_KALIPLARI:
        sarki_adi = sarki_adi.replace(kalip, "").replace(kalip.upper(), "")
    return sarki_adi.strip(" '\"")


# ═══════════════════════════════════════════════
# GENEL SOHBET (OpenRouter) — DB BAĞLAMIYLA
# ═══════════════════════════════════════════════

def genel_sohbet(metin: str, sistem_override: str = None) -> str:
    global _sohbet_gecmisi
    if not OPENROUTER_API_KEY:
        return None

    _db_gecmis_yukle()

    try:
        sistem = sistem_override or VERA_SISTEM_MESAJI_GUCLU

        try:
            sahip = kisi_bul("Alper")
            if sahip:
                yas = _yas_hesapla(sahip.get("dogum_tarihi"))
                sahip_bilgi = (
                    f"\n\nKULLANICI BİLGİSİ:\n"
                    f"Seninle konuşan: {sahip['isim']}.\n"
                    f"İlişki: {sahip.get('iliski', 'sahip')}.\n"
                )
                if yas is not None:
                    sahip_bilgi += f"Yaşı: {yas}.\n"
                sahip_bilgi += (
                    f"Notlar: {sahip.get('notlar', '')}.\n"
                    "Kullanıcının adını uygun yerlerde kullan, samimi ol."
                )
                sistem += sahip_bilgi
        except Exception:
            pass

        kisi_bilgisi = _kisi_bilgisi_ekle(metin)
        if kisi_bilgisi:
            sistem += f"\n\nBahsedilen kişi: {kisi_bilgisi}"

        db_baglamı = _db_gecmis_baglamini_hazirla(limit=15)
        if db_baglamı:
            sistem += db_baglamı

        mesajlar = [{"role": "system", "content": sistem}]
        mesajlar.extend(_sohbet_gecmisi[-_SOHBET_MAX:])
        mesajlar.append({"role": "user", "content": metin + "\n\n(Yanıtını Türkçe ver.)"})

        r = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENROUTER_MODEL,
                "messages": mesajlar,
                "max_tokens": 300,
                "temperature": 0.7,
                "top_p": 0.9,
            },
            timeout=20,
        )
        data = r.json()

        if r.status_code != 200:
            hata = data.get("error", {}).get("message", f"HTTP {r.status_code}")
            print(f"[OPENROUTER] Hata: {hata}")
            return "Sunucuya ulaşamadım, internet bağlantını kontrol eder misin?"

        yanit = data["choices"][0]["message"]["content"].strip()
        if not yanit:
            return "Bir yanıt alamadım, tekrar dener misin?"

        _sohbet_gecmisi.append({"role": "user",      "content": metin})
        _sohbet_gecmisi.append({"role": "assistant", "content": yanit})
        if len(_sohbet_gecmisi) > _SOHBET_MAX:
            _sohbet_gecmisi = _sohbet_gecmisi[-_SOHBET_MAX:]

        # Arka planda kişi tespiti yap
        if any(k in normalize_text(metin) for k in _KISI_ILISKI_KELIMELER):
            _arka_plan_kisi_tespit(metin, yanit)

        return yanit

    except requests.exceptions.Timeout:
        return "Yanıt geç geldi, tekrar dener misin?"
    except Exception as e:
        print(f"[OPENROUTER HATA] {e}")
        return "Bir hata oluştu, lütfen tekrar dener misin?"


# ═══════════════════════════════════════════════════════════════
# DIŞA AÇIK GİRİŞ NOKTASI
# ═══════════════════════════════════════════════════════════════

def komut_isle(metin: str) -> str:
    global _vera_uyanik, _sohbet_gecmisi, _db_gecmis_yuklendi
    m = normalize_text(metin)

    # ═══ 1. UYKU MODU ════════════════════════════════════════════
    if not _vera_uyanik:
        return None

    # ═══ 2b. BAĞLAMSAL BİRLEŞTİRME ══════════════════════════════
    try:
        son_yanit = son_yanit_getir()
        baglamsal_sonuc = _baglamsal_birlestir(son_yanit, metin)
        if baglamsal_sonuc is not None:
            print(f"[BAĞLAM] Önceki soru ile birleştirildi.")
            return baglamsal_sonuc
    except Exception as e:
        print(f"[BAĞLAM] Hata: {e}")

    # ═══ 3. GÜÇ ONAY KOMUTLARI ═══════════════════════════════════
    guc_durum, guc_yanit = guc_onay_kontrol(m)
    if guc_durum in ["iptal", "onay", "bekle"]:
        return guc_yanit

    # ═══ 3b. KİŞİ YÖNETİMİ ════════════════════════════════════════

    # Tüm kayıtlı kişileri listele
    if icerir(m, "kimleri taniyon", "kayitli kisiler", "kisi listesi",
              "kimleri hafizanda", "kisi var mi"):
        kisiler = tum_kisiler()
        if not kisiler:
            return "Henüz hafızamda kayıtlı kimse yok, Alper."
        isimler = ", ".join(
            k["isim"] + (f" ({k['iliski']})" if k.get("iliski") else "")
            for k in kisiler
        )
        return f"Şu kişileri tanıyorum: {isimler}."

    # Kişi kaydet / güncelle
    if icerir(m, "kaydet", "hatirla", "tani bunu", "kisi ekle",
              "not al", "hafizana al") and len(m.split()) >= 3:
        return _kisi_kaydet_komutu(metin)

    # Belirli ilişki kelimesiyle otomatik kayıt ("X benim annem")
    if icerir(m, "benim") and icerir(m, *_KISI_ILISKI_KELIMELER):
        return _kisi_kaydet_komutu(metin)

    # Kişiyi sil / unut
    _kisi_sil_tetik = (
        (icerir(m, "sil", "unut", "hafizandan sil", "kayittan sil") and
         icerir(m, "kisi", "isim", "bunu", "onu")) or
        (icerir(m, "unut") and any(k[0].isupper() for k in metin.split() if len(k) >= 2))
    )
    if _kisi_sil_tetik:
        return _kisi_sil_komutu(metin)

    # ═══ 4. SİSTEM KOMUTLARI ══════════════════════════════════════
    if icerir(m, "bilgisayari kapat", "pc kapat", "bilgisayar kapat",
              "sistemi kapat", "shutdown") and not _isik_komutu_mu(m):
        return bilgisayar_kapat_iste()

    if icerir(m, "yeniden basla", "restart", "reboot"):
        return bilgisayar_yeniden_baslatma_iste()

    if icerir(m, "bilgisayar uyu", "uyku moduna al", "sleep modu"):
        return bilgisayar_uyu()

    if icerir(m, "ekrani kilitle", "bilgisayari kilitle", "ekran kilidi"):
        return ekran_kilitle()

    if icerir(m, "sesi ac", "ses ac", "sesi geri ac", "sessizligi kapat"):
        return ses_ac_kapat(True)
    if icerir(m, "sesi kapat", "sessiz yap", "sustur", "sesi sus"):
        return ses_ac_kapat(False)

    if icerir(m, "ekran goruntusu", "screenshot", "ekrani yakala", "ss al"):
        return ekran_goruntusu()

    if icerir(m, "monitoru genislet", "monitörü genişlet", "ekrani genislet",
              "iki ekran", "extend mod", "extend yap", "her iki ekran"):
        return monitor_genislet()

    if icerir(m, "sadece ikinci ekran", "ikinci ekrani ac", "yan ekrani ac",
              "external mod", "sadece yan ekran", "ana ekrani kapat"):
        return monitor_sadece_ikinci()

    if icerir(m, "ekrani kopyala", "ekrani klonla", "mirror mod", "klon mod",
              "ayni goruntu", "ayni ekran", "ekrani cogalt"):
        return monitor_kopyala()

    if icerir(m, "monitoru daralt", "monitörü daralt", "yan ekrani kapat",
              "ikinci ekrani kapat", "tek ekran", "sadece ana ekran",
              "ana ekrana don", "internal mod"):
        return monitor_daralt()

    if icerir(m, "ses arttir", "sesi arttir", "sesi yukselt",
              "sesi ac biraz", "sesi acar misin biraz", "biraz ses ver"):
        return ses_arttir()

    if icerir(m, "ses azalt", "sesi azalt", "sesi dusur", "biraz kisalt",
              "sesi kisalt", "ses kisalt"):
        return ses_azalt()

    if icerir(m, "gorev yoneticisi", "task manager", "taskmgr"):
        return gorev_yoneticisi_ac()

    if icerir(m, "masaustu goster", "masaüstü göster", "pencereleri kucult",
              "tum pencereleri kucult", "masaustune don"):
        return masaustu_goster()

    if icerir(m, "bildirimleri ac", "bildirim merkezi", "bildirim ac",
              "notification center"):
        return bildirim_merkezi_ac()

    if icerir(m, "dosya gezgini", "explorer ac", "klasoru ac", "dosyalari goster"):
        return dosya_gezgini_ac()

    # ═══ 5. IŞIK KOMUTLARI ═══════════════════════════════════════
    if _isik_komutu_mu(m) and icerir(m, "parlaklik", "parlakliga", "parlakligi", "parlak"):
        sayi = re.search(r'\d+', m)
        if sayi:
            return ampul_parlaklik(max(1, min(100, int(sayi.group()))))
        return "Parlaklığı yüzde kaç yapalım? Örneğin: yüzde 80."

    if icerir(m, "parlaklik", "parlakliga", "parlakligi") and icerir(m, "yuzde"):
        sayi = re.search(r'\d+', m)
        if sayi:
            return ampul_parlaklik(max(1, min(100, int(sayi.group()))))

    if icerir(m, "isigi ac", "isik ac", "lamba ac", "lambay ac",
              "isigi yak", "lamba yak", "isigi acar misin", "isigi acabilir misin"):
        return ampul_ac()

    if _isik_komutu_mu(m) and icerir(m, "ac", "yak", "acar", "acabilir"):
        return ampul_ac()

    if icerir(m, "isigi kapat", "isik kapat", "lamba kapat",
              "isigi sondur", "lambay sondur", "isigi kapar misin"):
        return ampul_kapat()

    if _isik_komutu_mu(m) and icerir(m, "kapat", "sondur", "kapar"):
        return ampul_kapat()

    if _isik_renk_komutu_mu(m):
        for renk_n in COLORS:
            if renk_n in m:
                return ampul_renk(renk_n)
        return "Hangi rengi istiyorsun?"

    # ═══ 6. HAVA DURUMU ═══════════════════════════════════════════
    if icerir(m, "hava", "sicaklik", "yagmur mu", "hava nasil", "dis hava"):
        sehir = sehir_bul(m)
        if sehir:
            return hava_durumu(sehir)
        return "Hangi şehrin hava durumunu öğreneyim?"

    # ═══ 7. SAAT / TARİH ══════════════════════════════════════════
    if icerir(m, "saat kac", "saat nedir", "simdi saat"):
        return f"Saat şu an {time.strftime('%H:%M')}."

    if icerir(m, "bugun ne gun", "tarih nedir", "bugunun tarihi"):
        GUNLER = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        AYLAR  = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                  "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        lt = time.localtime()
        return f"Bugün {GUNLER[lt.tm_wday]}, {lt.tm_mday} {AYLAR[lt.tm_mon]} {lt.tm_year}."

    # ═══ 8. UYGULAMA AÇMA ═════════════════════════════════════════
    if icerir(m, "acar misin", "acabilir misin", "actirabilir misin") and not _isik_komutu_mu(m):
        goster = uygulama_bul(m)
        if goster:
            return uygulama_ac(goster)
        ham = uygulama_ham_bul(m)
        if ham and len(ham) >= 3:
            return uygulama_ac(ham.capitalize())
        return "Hangi uygulamayı açayım?"

    if icerir(m, "ac", "baslat", "calistir", "actir") \
            and not _isik_komutu_mu(m) \
            and not icerir(m, "ne", "nedir", "nasil", "niye", "neden", "hangi",
                           "kim", "soyle", "anlat", "bilgi", "hakkinda", "nerede", "kac"):
        goster = uygulama_bul(m)
        if goster:
            return uygulama_ac(goster)
        ham = uygulama_ham_bul(m)
        if ham and len(ham) >= 3:
            return uygulama_ac(ham.capitalize())

    # ═══ 9. SPOTIFY KOMUTLARI ══════════════════════════════════════

    # Sadece Spotify uygulamasını aç
    if icerir(m, "spotify ac", "spotifyi ac", "spotify'i ac", "spotify'yi ac",
              "spotify baslat", "spotifyi baslat"):
        return spotify_uygulamasi_ac()

    _SPOTIFY_CAL_KALIPLARI = [
        "sarki ac", "sarki cal", "cal sarki", "spotifyda cal", "spotifyda ac",
        "muzik ac", "muzik cal", "sarkiyi cal", "sarkiyi ac", "sarkisini cal",
    ]
    _SPOTIFY_ANAHTAR = ("sarki", "muzik", "spotify", "cal ", "calistir")

    _spotify_eslesme = (
        icerir(m, *_SPOTIFY_CAL_KALIPLARI)
        or (icerir(m, "spotify") and icerir(m, "cal", "ac", "calistir"))
        or (icerir(m, "cal") and icerir(m, *_SPOTIFY_ANAHTAR) and not _isik_komutu_mu(m))
        or (m.strip().endswith("cal") and not _isik_komutu_mu(m) and len(m.split()) >= 2)
    )

    if _spotify_eslesme and not _isik_komutu_mu(m):
        sarki_adi = _sarki_adi_temizle(metin)
        if sarki_adi and len(sarki_adi) > 1:
            return spotify_sarki_ac(sarki_adi)
        return "Hangi şarkıyı çalayım?"

    if icerir(m, "ne caliyor", "hangi sarki", "calan sarki", "su an ne caliyor"):
        return spotify_calani_ogren()

    if icerir(m, "sarkiyi durdur", "muzigi durdur", "calmayi durdur", "spotify durdur"):
        return spotify_durdur()

    if icerir(m, "sarkiya devam et", "calmaya devam et", "tekrar cal"):
        return spotify_cal()

    if icerir(m, "spotify sesi kapat", "spotify sustur"):
        return spotify_ses_ac(True)
    if icerir(m, "spotify sesi ac"):
        return spotify_ses_ac(False)

    # ═══ 10. YAŞ + KİŞİ YÖNETİMİ ═══════════════════════════════
    if icerir(m, "kac yasindayim", "yasim kac", "kac yasinda",
              "dogum tarihim", "ne zaman dogdum"):
        try:
            sahip = kisi_bul("Alper")
        except Exception:
            sahip = None
        if sahip and sahip.get("dogum_tarihi"):
            cumle = _yas_cumlesi(sahip["dogum_tarihi"], sahip.get("isim", "Alper"))
            return cumle or "Doğum tarihini bulamadım."
        return "Doğum tarihini henüz kaydetmemişiz galiba."

    if icerir(m, "kim", "taniyor musun", "hatirlıyor musun"):
        for kelime in metin.split():
            if len(kelime) >= 3 and kelime[0].isupper():
                try:
                    kisi = kisi_bul(kelime)
                    if kisi:
                        bilgi = kisi["isim"]
                        if kisi.get("iliski"): bilgi += f", senin {kisi['iliski']}"
                        if kisi.get("notlar"): bilgi += f". {kisi['notlar']}"
                        return f"Evet, {bilgi}."
                except Exception:
                    pass

    # ═══ 11. HIZLI YEREL CEVAPLAR ══════════════════════════════
    if icerir(m, "merhaba", "selam", "gunaydin", "iyi gunler", "iyi aksamlar"):
        saat = time.localtime().tm_hour
        if   6  <= saat < 12: return random.choice(["Günaydın! Ne yapalım?", "Günaydın!"])
        elif 12 <= saat < 18: return random.choice(["Merhaba! Ne yapalım?", "Merhaba, dinliyorum."])
        elif 18 <= saat < 22: return random.choice(["İyi akşamlar! Ne yapalım?", "İyi akşamlar."])
        else:                 return random.choice(["İyi geceler! Dinliyorum.", "İyi geceler!"])

    if icerir(m, "nasilsin", "nasil gidiyor", "iyi misin"):
        return random.choice([
            "İyiyim, teşekkürler! Sen nasılsın?",
            "Gayet iyi! Ne yapalım?",
            "Çok iyiyim! Bir şey sor.",
        ])

    if icerir(m, "tesekkur", "sagol", "eyvallah"):
        return random.choice([
            "Rica ederim!", "Ne demek, her zaman.", "Seve seve.",
        ])

    if icerir(m, "ne yapabilirsin", "neler biliyorsun", "yeteneklerin"):
        return (
            "Akla gelebilecek her konuda konuşabiliriz. Bilim, tarih, teknoloji, sağlık, "
            "hukuk, spor, yemek tarifleri, dil, felsefe, programlama, tarım... "
            "Bunların yanında ışığı kontrol eder, hava durumu söyler, uygulama açar, "
            "ekran görüntüsü alır, bilgisayarı yönetir ve sana özel kişileri hatırlarım."
        )

    if icerir(m, "hafizani temizle", "gecmisi sil", "sifirla"):
        _sohbet_gecmisi.clear()
        _db_gecmis_yuklendi = False
        return "Tamam, oturum hafızamı temizledim. Veritabanındaki geçmiş duruyor, sadece bu oturumu sıfırladım."

    # ═══ 12. YAPAY ZEKA ═════════════════════════════════════════
    yanit = genel_sohbet(metin)
    if yanit:
        return yanit

    return random.choice([
        "Anlayamadım, tekrar söyler misin?",
        "Ne dediğini tam anlamadım, bir daha söyler misin?",
        "Biraz daha açar mısın?",
    ])