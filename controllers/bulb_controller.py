import random
import time
from core.config import BULB_DEVICE_ID, BULB_LOCAL_KEY, BULB_IP, COLORS, COLORS_TR, BEYAZ_TONLAR

_ampul_durum = None
_ampul_son_komut = None 

DPS_SWITCH      = "20"  
DPS_MOD         = "21"   
DPS_PARLAKLIK   = "22"   
DPS_RENK_ISI    = "23"   
DPS_RENK_HSV    = "24"   

def _bulb():
    """Tuya ampul bağlantısı oluşturur."""
    try:
        import tinytuya
        d = tinytuya.BulbDevice(
            dev_id=BULB_DEVICE_ID,
            address=BULB_IP,
            local_key=BULB_LOCAL_KEY,
            version=3.3
        )
        d.set_socketTimeout(6)
        return d
    except Exception as e:
        print(f"[AMPUL BAĞLANTI] {e}")
        return None


def _yuzde_to_tuya(yuzde: int) -> int:
    """0-100 yüzde değerini Tuya'nın 10-1000 aralığına çevirir."""
    return max(10, min(1000, int(yuzde * 10)))


def _ampul_durum_guncelle():
    """Ampulün gerçek durumunu oku ve _ampul_durum'u güncelle."""
    global _ampul_durum
    b = _bulb()
    if b is None:
        return
    try:
        durum = b.status()
        dps = durum.get("dps", {})
        _ampul_durum = dps.get(DPS_SWITCH, False)
        print(f"[AMPUL] Durum güncellendi: {'AÇIK' if _ampul_durum else 'KAPALI'}")
    except Exception as e:
        print(f"[AMPUL] Durum okunamadı: {e}")


def ampul_ac() -> str:
    """Ampulü açar."""
    global _ampul_durum, _ampul_son_komut
    
    b = _bulb()
    if b is None:
        return "Ampule bağlanamadım."
    
    try:
        # Önce mevcut durumu kontrol et
        _ampul_durum_guncelle()
        if _ampul_durum is True:
            return random.choice([
                "Işık zaten açık.",
                "Işık zaten yanıyor.",
                "Açık zaten, başka bir şey istersen?",
            ])
        
        # AÇ komutunu gönder
        b.turn_on()
        time.sleep(0.2)
        
        # Başarılı oldu mu kontrol et
        _ampul_durum_guncelle()
        if _ampul_durum is True:
            _ampul_son_komut = "ac"
            return random.choice([
                "Tamam, ışığı açtım.",
                "Işığı yaktım.",
                "Oldu, ışık açık.",
                "Işık açıldı, buyur.",
                "Yaktım!",
                "Işık geldi, keyfine bak.",
            ])
        else:
            return "Işık açılamadı, tekrar dener misin?"
            
    except Exception as e:
        return f"Işık açılamadı: {e}"


def ampul_kapat() -> str:
    """Ampulü kapatır."""
    global _ampul_durum, _ampul_son_komut
    
    b = _bulb()
    if b is None:
        return "Ampule bağlanamadım."
    
    try:
        # Önce mevcut durumu kontrol et
        _ampul_durum_guncelle()
        if _ampul_durum is False:
            return random.choice([
                "Işık zaten kapalı.",
                "Işık zaten söndürülmüş.",
                "Zaten kapalı, başka bir şey?",
            ])
        
        # KAPAT komutunu gönder
        b.turn_off()
        time.sleep(0.2)
        
        # Başarılı oldu mu kontrol et
        _ampul_durum_guncelle()
        if _ampul_durum is False:
            _ampul_son_komut = "kapat"
            return random.choice([
                "Tamam, ışığı kapattım.",
                "Işığı söndürdüm.",
                "Oldu, ışık kapalı.",
                "Kapattım, karanlık oldu.",
                "Söndürdüm, yeterli mi?",
            ])
        else:
            return "Işık kapatılamadı, tekrar dener misin?"
            
    except Exception as e:
        return f"Işık kapatılamadı: {e}"


def ampul_renk(renk_n: str) -> str:
    """Ampul rengini değiştirir."""
    global _ampul_durum, _ampul_son_komut
    
    if renk_n not in COLORS:
        return "Bu rengi tanımıyorum."
    
    b = _bulb()
    if b is None:
        return "Ampule bağlanamadım."
    
    try:
        # Önce ışığı aç
        b.turn_on()
        time.sleep(0.2)
        
        if renk_n in BEYAZ_TONLAR:
            ct = BEYAZ_TONLAR[renk_n]
            b.set_multiple_values({
                DPS_MOD: "white",
                DPS_PARLAKLIK: 1000,
                DPS_RENK_ISI: ct,
                DPS_SWITCH: True,
            })
        else:
            r, g, bl = COLORS[renk_n]
            # HSV formatına çevir ve gönder
            b.set_colour(r, g, bl)
            time.sleep(0.1)
            # Açık olduğundan emin ol
            b.turn_on()
        
        _ampul_durum = True
        _ampul_son_komut = f"renk_{renk_n}"
        
        renk_goster = COLORS_TR.get(renk_n, renk_n)
        return random.choice([
            f"Tamam, ışığı {renk_goster} yaptım.",
            f"Oldu! Işık şimdi {renk_goster}.",
            f"{renk_goster.capitalize()} renk ayarlandı.",
            f"Işık {renk_goster} oldu, hoş görünüyor.",
        ])
    except Exception as e:
        return f"Renk değiştirilemedi: {e}"


def ampul_parlaklik(yuzde: int) -> str:
    """
    Ampul parlaklığını ayarlar - SAĞLAM SÜRÜM
    """
    global _ampul_durum, _ampul_son_komut
    
    # Yüzde değerini kontrol et
    yuzde = max(0, min(100, yuzde))
    
    b = _bulb()
    if b is None:
        return "Ampule bağlanamadım."
    
    try:
        tuya_deger = _yuzde_to_tuya(yuzde)
        
        # ═══ 1. ADIM: Önce ampulü aç ═══
        print(f"[AMPUL] Parlaklık {yuzde}% ayarlanıyor...")
        
        # Ampulü aç
        b.turn_on()
        time.sleep(0.3)
        _ampul_durum = True
        
        # ═══ 2. ADIM: Mevcut modu öğren ═══
        mevcut_mod = None
        hsv_str = None
        
        for deneme in range(3):  # 3 kere dene
            try:
                durum = b.status()
                dps = durum.get("dps", {})
                mevcut_mod = dps.get(DPS_MOD, "white")
                hsv_str = dps.get(DPS_RENK_HSV, "")
                print(f"[AMPUL] Mod: {mevcut_mod}, HSV: {hsv_str}")
                break
            except Exception as e:
                print(f"[AMPUL] Durum okuma deneme {deneme+1}: {e}")
                time.sleep(0.2)
        
        if mevcut_mod is None:
            mevcut_mod = "white"
        
        # ═══ 3. ADIM: Moda göre parlaklık ayarla ═══
        basarili = False
        
        if mevcut_mod == "colour" and hsv_str and len(hsv_str) == 12:
            # Colour modu - HSV üzerinden parlaklık ayarla
            try:
                h = hsv_str[0:4]
                s = hsv_str[4:8]
                v = format(tuya_deger, "04x")
                
                b.set_multiple_values({
                    DPS_RENK_HSV: h + s + v,
                    DPS_SWITCH: True,
                })
                time.sleep(0.2)
                basarili = True
                print(f"[AMPUL] HSV ile parlaklık ayarlandı: {h}{s}{v}")
            except Exception as e:
                print(f"[AMPUL] HSV hatası: {e}, white moduna geçiliyor")
                mevcut_mod = "white"
        
        if not basarili:
            # White modu - doğrudan DPS 22
            try:
                b.set_multiple_values({
                    DPS_MOD: "white",
                    DPS_PARLAKLIK: tuya_deger,
                    DPS_SWITCH: True,
                })
                time.sleep(0.2)
                basarili = True
                print(f"[AMPUL] White modunda parlaklık ayarlandı: {tuya_deger}")
            except Exception as e:
                print(f"[AMPUL] White mod hatası: {e}")
                
                # Son çare: direk turn_on ile yeniden başlat
                try:
                    b.turn_on()
                    time.sleep(0.3)
                    b.set_multiple_values({
                        DPS_MOD: "white",
                        DPS_PARLAKLIK: tuya_deger,
                        DPS_SWITCH: True,
                    })
                    basarili = True
                    print(f"[AMPUL] Yeniden başlatma ile parlaklık ayarlandı")
                except Exception as e2:
                    print(f"[AMPUL] Son çare hatası: {e2}")
                    return f"Parlaklık ayarlanamadı: {e2}"
        
        # ═══ 4. ADIM: Başarılı mı kontrol et ═══
        if basarili:
            _ampul_durum = True
            _ampul_son_komut = f"parlaklik_{yuzde}"
            
            return random.choice([
                f"Tamam, parlaklık yüzde {yuzde} oldu.",
                f"Parlaklık yüzde {yuzde} ayarlandı.",
                f"Oldu! Işık yüzde {yuzde} parlaklıkta.",
                f"Parlaklık {yuzde} yapıldı.",
                f"{yuzde} yaptım, istediğin gibi mi?",
            ])
        else:
            return "Parlaklık ayarlanamadı, tekrar dener misin?"
            
    except Exception as e:
        print(f"[AMPUL] Parlaklık hatası: {e}")
        
        # ═══ KRİTİK: Hata durumunda ampulü yeniden başlatmayı dene ═══
        try:
            print("[AMPUL] Kurtarma modu: ampul yeniden başlatılıyor...")
            b.turn_off()
            time.sleep(1)
            b.turn_on()
            time.sleep(0.5)
            b.set_multiple_values({
                DPS_MOD: "white",
                DPS_PARLAKLIK: _yuzde_to_tuya(yuzde),
                DPS_SWITCH: True,
            })
            _ampul_durum = True
            return f"Kurtarma yapıldı, parlaklık yüzde {yuzde} oldu."
        except Exception as e2:
            print(f"[AMPUL] Kurtarma hatası: {e2}")
            return f"Parlaklık ayarlanamadı: {e}"


def ampul_durum_goster() -> str:
    """Geliştirme/debug için ampulün raw DPS durumunu döndürür."""
    b = _bulb()
    if b is None:
        return "Ampule bağlanamadım."
    try:
        durum = b.status()
        dps = durum.get("dps", {})
        return f"""
DPS Durumu:
Switch: {dps.get(DPS_SWITCH, '?')}
Mod: {dps.get(DPS_MOD, '?')}
Parlaklık: {dps.get(DPS_PARLAKLIK, '?')}
Renk Isı: {dps.get(DPS_RENK_ISI, '?')}
HSV: {dps.get(DPS_RENK_HSV, '?')}
Raw: {durum}
"""
    except Exception as e:
        return f"Durum alınamadı: {e}"


def ampul_test():
    """Ampul test fonksiyonu - parlaklığı sırayla değiştirir."""
    print("[TEST] Ampul testi başlıyor...")
    for yuzde in [10, 30, 50, 70, 100]:
        print(f"[TEST] {yuzde}% deneniyor...")
        sonuc = ampul_parlaklik(yuzde)
        print(f"[TEST] Sonuç: {sonuc}")
        time.sleep(2)
    print("[TEST] Test tamamlandı.")