# ══════════════════════════════════════════════════════════════
# SİSTEM KONTROL KOMUTLARI
# ══════════════════════════════════════════════════════════════

import time
import random
import subprocess
import threading
import os
from datetime import datetime
from core.config import GUC_ONAY_SURE


_guc_onay = {"islem": None, "zaman": 0}


def _guc_onay_temizle():
    _guc_onay["islem"] = None
    _guc_onay["zaman"] = 0


def bilgisayar_kapat_iste() -> str:
    """Bilgisayarı kapatmak için onay ister."""
    _guc_onay["islem"] = "kapat"
    _guc_onay["zaman"] = time.time()
    return random.choice([
        "Bilgisayarı kapatmamı istiyorsun, değil mi? Emin isen 'evet' ya da 'onaylıyorum' de, iptal için 'hayır' de.",
        "Tamam, ama kapatmadan önce onayını alayım. Devam etmemi istersen 'evet' de.",
        "Kapatma işlemini başlatmadan önce onayını bekliyorum. 'Evet' veya 'hayır'?",
        "Bilgisayar kapanacak, emin misin? Onaylıyorsan 'evet' de.",
    ])


def bilgisayar_yeniden_baslatma_iste() -> str:
    """Bilgisayarı yeniden başlatmak için onay ister."""
    _guc_onay["islem"] = "yeniden_basla"
    _guc_onay["zaman"] = time.time()
    return random.choice([
        "Bilgisayarı yeniden başlatmamı istiyorsun, değil mi? Emin isen 'evet' ya da 'onaylıyorum' de.",
        "Yeniden başlayacağım ama önce onayını alayım. Devam için 'evet' de.",
        "Yeniden başlatma onayı bekliyorum. 'Evet' dersen başlıyorum.",
        "Sistem yeniden başlayacak, onaylıyor musun?",
    ])


def bilgisayar_kapat_onayla() -> str:
    """Bilgisayarı kapatır."""
    _guc_onay_temizle()
    try:
        subprocess.Popen("shutdown /s /t 5", shell=True)
        return random.choice([
            "Tamam, bilgisayar 5 saniye içinde kapanıyor. Güle güle!",
            "Kapatıyorum, görüşürüz!",
            "5 saniye sonra kapanıyor, iyi günler!",
        ])
    except Exception as e:
        return f"Kapatma başlatılamadı: {e}"


def bilgisayar_yeniden_baslatma_onayla() -> str:
    """Bilgisayarı yeniden başlatır."""
    _guc_onay_temizle()
    try:
        subprocess.Popen("shutdown /r /t 5", shell=True)
        return random.choice([
            "Tamam, bilgisayar 5 saniye içinde yeniden başlıyor.",
            "Yeniden başlatıyorum, birazdan görüşürüz!",
            "Sistem yeniden başlıyor, 5 saniye içinde.",
        ])
    except Exception as e:
        return f"Yeniden başlama başlatılamadı: {e}"


def bilgisayar_uyu() -> str:
    """Bilgisayarı uyku moduna alır."""
    try:
        subprocess.Popen("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
        return random.choice([
            "Tamam, bilgisayarı uyku moduna alıyorum.",
            "Bilgisayar uyuyor. Devam etmek için bir tuşa bas.",
            "Uyku modu etkinleştirildi.",
            "Uyutuyorum, uyanmak için tuşla.",
            "Sistem uyku modunda, kolay gelsin.",
        ])
    except Exception as e:
        return f"Uyku modu başlatılamadı: {e}"


def ekran_kilitle() -> str:
    """Ekranı kilitler."""
    try:
        subprocess.Popen("rundll32.exe user32.dll,LockWorkStation", shell=True)
        return random.choice([
            "Tamam, ekranı kilitledim.",
            "Ekran kilitleniyor.",
            "Ekran kilidi etkin.",
            "Kilitledim, kimse görmesin!",
            "Ekran güvende, şifreni unutma.",
        ])
    except Exception as e:
        return f"Ekran kilitlenemedi: {e}"


def ses_ac_kapat(ses_ac: bool) -> str:
    """Sesi açar veya kapatır."""
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMute(0 if ses_ac else 1, None)
        return "Ses açıldı." if ses_ac else "Ses kapatıldı."
    except Exception:
        pass
    try:
        import pyautogui
        pyautogui.press("volumemute")
        return "Ses durumu değiştirildi."
    except Exception as e:
        return f"Ses değiştirilemedi: {e}"


def ekran_goruntusu() -> str:
    """Ekran görüntüsü alır."""
    def _al():
        time.sleep(0.2)
        try:
            import pyautogui
            dosya_adi = os.path.join(
                os.path.expanduser("~"), "Desktop",
                f"vera_ekran_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            screenshot = pyautogui.screenshot()
            screenshot.save(dosya_adi)
        except Exception as e:
            print(f"[EKRAN] {e}")

    threading.Thread(target=_al, daemon=True).start()
    return random.choice([
        "Ekran görüntüsü alındı ve masaüstüne kaydedildi.",
        "Tamam, ekranı yakaladım. Masaüstünde bulabilirsin.",
        "Ekran fotoğrafı masaüstüne kaydedildi.",
        "İşte! Ekranın fotoğrafı masaüstünde seni bekliyor.",
        "Çektiğim ekran görüntüsünü masaüstüne bıraktım.",
        "Gördüğümü yakaladım. Dosya masaüstünde.",
        "Ekranı dondurdum. Masaüstüne kaydettim.",
        "Oldu, ekran görüntüsü masaüstünde hazır.",
        "Tıpkı bir fotoğraf gibi! Masaüstüne koydum.",
        "İstediğin ekran görüntüsünü aldım. Masaüstünde.",
        "Anlık görüntü masaüstüne kaydedildi.",
        "Poz yakalandı! Dosyayı masaüstünde bulabilirsin.",
        "Ekran görüntünü aldım, masaüstüne baktığında göreceksin.",
        "Gördüğün her şeyi fotoğrafladım. Masaüstünde!",
        "Anı yakaladım! Masaüstüne kaydettim.",
    ])


def monitor_genislet() -> str:
    """Her iki ekranı extend (genişlet) moduna alır."""
    try:
        subprocess.Popen("DisplaySwitch.exe /extend", shell=True)
        return random.choice([
            "Ekran genişletildi, her iki monitör aktif.",
            "Extend moduna geçildi.",
            "İki ekran genişletilmiş modda çalışıyor.",
            "Tamam, masaüstü iki ekrana yayıldı.",
        ])
    except Exception as e:
        return f"Monitör ayarlanamadı: {e}"


def monitor_daralt() -> str:
    """Sadece ana ekrana döner (PC screen only)."""
    try:
        subprocess.Popen("DisplaySwitch.exe /internal", shell=True)
        return random.choice([
            "Yan monitör kapatıldı, sadece ana ekran aktif.",
            "Tek ekran moduna geçildi.",
            "Ana ekrana döndüm, yan monitör kapalı.",
            "Yan monitör devre dışı.",
        ])
    except Exception as e:
        return f"Monitör ayarlanamadı: {e}"


def monitor_sadece_ikinci() -> str:
    """Sadece ikinci ekranı açık bırakır, ana ekranı kapatır."""
    try:
        subprocess.Popen("DisplaySwitch.exe /external", shell=True)
        return random.choice([
            "Tamam, sadece ikinci ekran aktif. Ana ekran kapatıldı.",
            "İkinci ekran moduna geçildi.",
            "Yan monitör açık, ana ekran kapalı.",
            "Sadece ikinci ekran çalışıyor.",
        ])
    except Exception as e:
        return f"Monitör ayarlanamadı: {e}"


def monitor_kopyala() -> str:
    """Her iki ekranda aynı görüntüyü gösterir (clone/mirror modu)."""
    try:
        subprocess.Popen("DisplaySwitch.exe /clone", shell=True)
        return random.choice([
            "Ekranlar kopyalandı, her ikisinde aynı görüntü var.",
            "Klonlama moduna geçildi.",
            "İki ekran da aynı görüntüyü gösteriyor.",
            "Mirror modu aktif.",
        ])
    except Exception as e:
        return f"Monitör ayarlanamadı: {e}"


def ses_arttir(adim: int = 5) -> str:
    """Sistem sesini artırır."""
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current = volume.GetMasterVolumeLevelScalar()
        new_vol = min(1.0, current + adim / 100.0)
        volume.SetMasterVolumeLevelScalar(new_vol, None)
        return f"Ses yüzde {int(new_vol * 100)}'e çıkarıldı."
    except Exception:
        pass
    try:
        import pyautogui
        for _ in range(adim // 2 or 1):
            pyautogui.press("volumeup")
        return "Ses artırıldı."
    except Exception as e:
        return f"Ses artırılamadı: {e}"


def ses_azalt(adim: int = 5) -> str:
    """Sistem sesini azaltır."""
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current = volume.GetMasterVolumeLevelScalar()
        new_vol = max(0.0, current - adim / 100.0)
        volume.SetMasterVolumeLevelScalar(new_vol, None)
        return f"Ses yüzde {int(new_vol * 100)}'e düşürüldü."
    except Exception:
        pass
    try:
        import pyautogui
        for _ in range(adim // 2 or 1):
            pyautogui.press("volumedown")
        return "Ses azaltıldı."
    except Exception as e:
        return f"Ses azaltılamadı: {e}"


def gorev_yoneticisi_ac() -> str:
    """Görev yöneticisini açar."""
    try:
        subprocess.Popen("taskmgr.exe", shell=True)
        return random.choice([
            "Görev yöneticisi açılıyor.",
            "Tamam, görev yöneticisi geliyor.",
        ])
    except Exception as e:
        return f"Görev yöneticisi açılamadı: {e}"


def masaustu_goster() -> str:
    """Masaüstünü gösterir (Win+D)."""
    try:
        import pyautogui
        pyautogui.hotkey("win", "d")
        return random.choice([
            "Masaüstü gösteriliyor.",
            "Tüm pencereler küçültüldü.",
            "Masaüstüne döndüm.",
        ])
    except Exception as e:
        return f"Masaüstü gösterilemedi: {e}"


def bildirim_merkezi_ac() -> str:
    """Windows bildirim merkezini açar (Win+A)."""
    try:
        import pyautogui
        pyautogui.hotkey("win", "a")
        return random.choice([
            "Bildirim merkezi açıldı.",
            "İşte bildirimler.",
        ])
    except Exception as e:
        return f"Bildirim merkezi açılamadı: {e}"


def dosya_gezgini_ac() -> str:
    """Dosya gezginini açar."""
    try:
        subprocess.Popen("explorer.exe", shell=True)
        return random.choice([
            "Dosya gezgini açılıyor.",
            "Tamam, Explorer geliyor.",
        ])
    except Exception as e:
        return f"Dosya gezgini açılamadı: {e}"


def guc_onay_kontrol(metin_n: str) -> tuple:
    """Güç onay durumunu kontrol eder ve onay/iptal işlemlerini yönetir."""
    from utils import icerir
    
    if _guc_onay["islem"] is None or time.time() - _guc_onay["zaman"] >= GUC_ONAY_SURE:
        return None, None
    
    # İptal kontrolü
    if icerir(metin_n, "hayir", "iptal", "vazgec", "birak", "durdur", 
              "durur", "olmaz", "istemiyorum", "bekle", "dur"):
        _guc_onay_temizle()
        return "iptal", random.choice([
            "Tamam, iptal ettim.",
            "Anlaşıldı, vazgeçtim.",
            "İptal edildi.",
            "Tamam, vazgeçtim.",
        ])

    # Onay kontrolü
    if icerir(metin_n, "evet", "onayli", "onayliyorum", "onay", "onayla",
              "kapat", "baslat", "devam", "tamam", "olsun",
              "kesinlikle", "tabii", "elbette", "yap", "oldu", "peki", 
              "hadi", "haydi", "yapabilirsin", "yapsın", "yapsin", 
              "evet yap", "evet kapat", "evet baslat", "dogru", "doğru", "tabi"):
        if _guc_onay["islem"] == "kapat":
            return "onay", bilgisayar_kapat_onayla()
        if _guc_onay["islem"] == "yeniden_basla":
            return "onay", bilgisayar_yeniden_baslatma_onayla()

    # Ne onay ne iptal - hatırlat
    return "bekle", random.choice([
        "Onaylamak için 'evet', iptal için 'hayır' de.",
        "Devam etmemi istiyorsan 'evet' de.",
        "Kararını bekliyorum, 'evet' veya 'hayır'?",
    ])