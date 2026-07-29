# ══════════════════════════════════════════════════════════════
# YARDIMCI FONKSİYONLAR
# ══════════════════════════════════════════════════════════════

import random
from core.config import CITIES, UYGULAMALAR, _TR_EKLER


def normalize_text(s: str) -> str:
    """Metni normalize eder: küçült, Türkçe karakterleri dönüştür."""
    s = s.replace("İ", "i").replace("I", "i")
    return (s.lower()
            .replace("ı", "i").replace("ğ", "g").replace("ş", "s")
            .replace("ç", "c").replace("ü", "u").replace("ö", "o"))


def icerir(metin_n: str, *kelimeler) -> bool:
    """Normalize edilmiş metinde kelimelerden biri geçiyor mu kontrol eder."""
    for k in kelimeler:
        if normalize_text(k) in metin_n:
            return True
    return False


def sehir_bul(metin_n: str):
    """Metinde şehir adı var mı kontrol eder."""
    metin_bitisik = metin_n.replace(" ", "")
    for anahtar in sorted(CITIES, key=len, reverse=True):
        anahtar_n = normalize_text(anahtar)
        if anahtar_n in metin_n or anahtar_n.replace(" ", "") in metin_bitisik:
            return anahtar
    return None


def ek_soy(kelime: str) -> list:
    """Türkçe ekleri temizleyerek kelimenin kök hallerini döndürür."""
    sonuclar = [kelime]
    for ek in _TR_EKLER:
        if kelime.endswith(ek) and len(kelime) - len(ek) >= 3:
            kok = kelime[:-len(ek)]
            if kok not in sonuclar:
                sonuclar.append(kok)
    return sonuclar


def uygulama_bul(metin_n: str):
    """Metinden uygulama ismi bulur."""
    for anahtar in sorted(UYGULAMALAR, key=len, reverse=True):
        if normalize_text(anahtar) in metin_n:
            return UYGULAMALAR[anahtar]
    for kelime in metin_n.split():
        for kok in ek_soy(kelime):
            if kok in UYGULAMALAR:
                return UYGULAMALAR[kok]
    return None


def uygulama_ham_bul(metin_n: str):
    """Metinden uygulama ismi çıkarmaya çalışır (ham)."""
    tetikleyiciler = {"ac", "baslat", "calistir", "actir", "acabilir", "misin",
                      "lutfen", "bir", "de", "da", "bana", "simdi", "hemen"}
    kelimeler = [k for k in metin_n.split() if k not in tetikleyiciler and len(k) > 2]
    if kelimeler:
        son = kelimeler[-1]
        kokler = ek_soy(son)
        return kokler[-1] if len(kokler) > 1 else son
    return None


def rastgele_cevap(cevaplar: list) -> str:
    """Listeden rastgele bir cevap seçer."""
    return random.choice(cevaplar)