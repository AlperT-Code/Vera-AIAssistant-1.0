# ══════════════════════════════════════════════════════════════
# VERİTABANI MODÜLÜ
# ══════════════════════════════════════════════════════════════

import os
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host":      os.getenv("DB_HOST", "localhost"),
    "user":      os.getenv("DB_USER", "root"),
    "password":  os.getenv("DB_PASSWORD", ""),
    "database":  os.getenv("DB_NAME", "vera_db"),
    "charset":   "utf8mb4",
    "collation": "utf8mb4_turkish_ci",
}


# ═══════════════════════════════════════════════
# BAĞLANTI
# ═══════════════════════════════════════════════

def db_baglan():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        print(f"[DB] Bağlantı hatası: {e}")
        return None


# ═══════════════════════════════════════════════
# SOHBET GEÇMİŞİ
# ═══════════════════════════════════════════════

def sohbet_kaydet(kullanici_mesaji: str, vera_yaniti: str, kisi_id: int = None) -> bool:
    """
    Sohbeti veritabanına kaydeder.
    Aynı mesaj son 5 dakika içinde zaten kayıtlıysa ATLAR.
    """
    conn = db_baglan()
    if not conn:
        return False
    try:
        cursor = conn.cursor()

        # ── Mükerrer kayıt kontrolü ──────────────────────────────
        cursor.execute(
            """
            SELECT COUNT(*) FROM sohbet_gecmisi
            WHERE kullanici_mesaji = %s
            AND tarih > DATE_SUB(NOW(), INTERVAL 5 MINUTE)
            """,
            (kullanici_mesaji[:2000],)
        )
        if cursor.fetchone()[0] > 0:
            print(f"[DB] Mükerrer kayıt atlandı: {kullanici_mesaji[:40]}")
            return False

        cursor.execute(
            """
            INSERT INTO sohbet_gecmisi (kisi_id, kullanici_mesaji, vera_yaniti)
            VALUES (%s, %s, %s)
            """,
            (kisi_id, kullanici_mesaji[:2000], vera_yaniti[:2000])
        )
        conn.commit()
        print(f"[DB] Kaydedildi: {kullanici_mesaji[:40]}")
        return True

    except mysql.connector.Error as e:
        print(f"[DB] Kayıt hatası: {e}")
        return False
    finally:
        conn.close()


def gecmis_getir(limit: int = 30) -> list:
    """
    Son N sohbeti eskiden yeniye sıralı döndürür.
    Her eleman: {"kullanici_mesaji": ..., "vera_yaniti": ...}
    """
    conn = db_baglan()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT kullanici_mesaji, vera_yaniti
            FROM sohbet_gecmisi
            ORDER BY tarih DESC
            LIMIT %s
            """,
            (limit,)
        )
        return list(reversed(cursor.fetchall()))
    except mysql.connector.Error as e:
        print(f"[DB] Geçmiş okuma hatası: {e}")
        return []
    finally:
        conn.close()


def son_yanit_getir() -> str:
    """En son Vera yanıtını döndürür (bekleyen soru kontrolü için)."""
    conn = db_baglan()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT vera_yaniti FROM sohbet_gecmisi
            ORDER BY tarih DESC LIMIT 1
            """
        )
        satir = cursor.fetchone()
        return satir[0] if satir else None
    except mysql.connector.Error as e:
        print(f"[DB] Son yanıt hatası: {e}")
        return None
    finally:
        conn.close()


def baglamsal_gecmis_getir(n: int = 3) -> list:
    """
    Son N tur sohbeti (kullanıcı + Vera) sıralı döndürür.
    Bağlamsal birleştirme için kullanılır.
    Örnek dönüş:
      [
        {"rol": "kullanici", "icerik": "Hadise şarkısı aç"},
        {"rol": "vera",      "icerik": "Hangi Hadise şarkısını çalayım?"},
        {"rol": "kullanici", "icerik": "Yaz Günü 2"},
      ]
    """
    conn = db_baglan()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT kullanici_mesaji, vera_yaniti
            FROM sohbet_gecmisi
            ORDER BY tarih DESC
            LIMIT %s
            """,
            (n,)
        )
        satirlar = list(reversed(cursor.fetchall()))
        sonuc = []
        for s in satirlar:
            sonuc.append({"rol": "kullanici", "icerik": s["kullanici_mesaji"]})
            sonuc.append({"rol": "vera",      "icerik": s["vera_yaniti"]})
        return sonuc
    except mysql.connector.Error as e:
        print(f"[DB] Bağlamsal geçmiş hatası: {e}")
        return []
    finally:
        conn.close()


def sohbet_ara(anahtar: str, limit: int = 5) -> list:
    """Geçmiş sohbetlerde anahtar kelime ara."""
    conn = db_baglan()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT kullanici_mesaji, vera_yaniti, tarih
            FROM sohbet_gecmisi
            WHERE kullanici_mesaji LIKE %s OR vera_yaniti LIKE %s
            ORDER BY tarih DESC
            LIMIT %s
            """,
            (f"%{anahtar}%", f"%{anahtar}%", limit)
        )
        return cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"[DB] Arama hatası: {e}")
        return []
    finally:
        conn.close()


def ayni_soru_daha_once_soruldu_mu(metin: str, dakika: int = 60) -> str | None:
    """
    Aynı (veya çok benzer) mesaj son X dakika içinde sorulmuş mu?
    Sorulmuşsa o zamanki Vera yanıtını döndürür, yoksa None.
    Böylece komut_isle() direkt DB cevabını kullanabilir, AI'ya gitmez.
    """
    conn = db_baglan()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT vera_yaniti FROM sohbet_gecmisi
            WHERE kullanici_mesaji = %s
            AND tarih > DATE_SUB(NOW(), INTERVAL %s MINUTE)
            ORDER BY tarih DESC
            LIMIT 1
            """,
            (metin[:2000], dakika)
        )
        satir = cursor.fetchone()
        return satir[0] if satir else None
    except mysql.connector.Error as e:
        print(f"[DB] Tekrar soru kontrolü hatası: {e}")
        return None
    finally:
        conn.close()


# ═══════════════════════════════════════════════
# KİŞİLER
# ═══════════════════════════════════════════════

def kisi_ekle(isim: str, iliski: str = None, dogum_tarihi: str = None, notlar: str = None) -> bool:
    conn = db_baglan()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        dt = None
        if dogum_tarihi:
            for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
                try:
                    dt = datetime.strptime(dogum_tarihi, fmt).date(); break
                except ValueError:
                    pass
        cursor.execute(
            "INSERT INTO kisiler (isim, iliski, dogum_tarihi, notlar) VALUES (%s,%s,%s,%s)",
            (isim, iliski, dt, notlar)
        )
        conn.commit()
        print(f"[DB] '{isim}' eklendi.")
        return True
    except mysql.connector.Error as e:
        print(f"[DB] Kişi ekleme hatası: {e}")
        return False
    finally:
        conn.close()


def kisi_guncelle(isim: str, iliski: str = None, dogum_tarihi: str = None, notlar: str = None) -> bool:
    conn = db_baglan()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        dt = None
        if dogum_tarihi:
            for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
                try:
                    dt = datetime.strptime(dogum_tarihi, fmt).date(); break
                except ValueError:
                    pass
        cursor.execute(
            """
            UPDATE kisiler
            SET iliski       = COALESCE(%s, iliski),
                dogum_tarihi = COALESCE(%s, dogum_tarihi),
                notlar       = COALESCE(%s, notlar)
            WHERE isim LIKE %s
            """,
            (iliski, dt, notlar, f"%{isim}%")
        )
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as e:
        print(f"[DB] Güncelleme hatası: {e}")
        return False
    finally:
        conn.close()


def kisi_bul(isim: str) -> dict:
    conn = db_baglan()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, isim, iliski, dogum_tarihi, notlar
            FROM kisiler WHERE isim LIKE %s
            ORDER BY olusturma_tarihi DESC LIMIT 1
            """,
            (f"%{isim}%",)
        )
        return cursor.fetchone()
    except mysql.connector.Error as e:
        print(f"[DB] Kişi arama hatası: {e}")
        return None
    finally:
        conn.close()


def tum_kisiler() -> list:
    conn = db_baglan()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, isim, iliski, dogum_tarihi, notlar FROM kisiler ORDER BY isim ASC"
        )
        return cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"[DB] Listeleme hatası: {e}")
        return []
    finally:
        conn.close()


def kisi_sil(isim: str) -> bool:
    conn = db_baglan()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM kisiler WHERE isim LIKE %s", (f"%{isim}%",))
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as e:
        print(f"[DB] Silme hatası: {e}")
        return False
    finally:
        conn.close()


# ═══════════════════════════════════════════════
# VERİTABANI DURUMU
# ═══════════════════════════════════════════════

def db_durum() -> str:
    conn = db_baglan()
    if not conn:
        return "Veritabanına bağlanılamıyor."
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sohbet_gecmisi")
        s = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM kisiler")
        k = cursor.fetchone()[0]
        return f"Veritabanı aktif. {s} sohbet, {k} kişi kayıtlı."
    except mysql.connector.Error as e:
        return f"Veritabanı hatası: {e}"
    finally:
        conn.close()