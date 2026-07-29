# ══════════════════════════════════════════════════════════════
# SES TANIMA VE SENTEZ
# ══════════════════════════════════════════════════════════════

import os
import time
import tempfile
import asyncio
import threading

from core.config import EDGE_TTS_VOICE

# Global değişkenler
_konusuyor = False
_konusma_cb = None
_tts_cache = {}
_mikrofon_aktif = True
_mikrofon_kilit = threading.Lock()
_konusma_kilidi = threading.Lock()
_konusma_baslangic_zamani = 0
_KONUSMA_BEKLEME_SURESI = 1.5

# Spotify ses kısma (ducking)
_duck_onceki_ses = None
_duck_kilidi = threading.Lock()


def _spotify_duck():
    """Konuşma algılandığında Spotify sesini %10'a kıs."""
    global _duck_onceki_ses
    with _duck_kilidi:
        if _duck_onceki_ses is not None:
            return
        try:
            from pycaw.pycaw import AudioUtilities
            for s in AudioUtilities.GetAllSessions():
                if s.Process and "spotify" in s.Process.name().lower():
                    vol = s.SimpleAudioVolume
                    mevcut = vol.GetMasterVolume()
                    if mevcut > 0.15:
                        _duck_onceki_ses = mevcut
                        vol.SetMasterVolume(0.10, None)
                    break
        except Exception:
            pass


def _spotify_unduck():
    """Konuşma bittikten sonra Spotify sesini eski haline getir."""
    global _duck_onceki_ses
    with _duck_kilidi:
        if _duck_onceki_ses is None:
            return
        onceki = _duck_onceki_ses
        _duck_onceki_ses = None
    try:
        from pycaw.pycaw import AudioUtilities
        for s in AudioUtilities.GetAllSessions():
            if s.Process and "spotify" in s.Process.name().lower():
                s.SimpleAudioVolume.SetMasterVolume(onceki, None)
                break
    except Exception:
        pass

# Vera'nın söylediği son metinleri tutan liste
_son_vera_metinleri = []
_son_vera_kilidi = threading.Lock()
_VERA_METIN_SURE = 20  # Saniye — bu süre içinde algılanırsa filtrele


def _vera_metin_ekle(metin: str):
    """Vera'nın söylediği metni kaydet"""
    with _son_vera_kilidi:
        _son_vera_metinleri.append({
            "metin": metin.lower().strip(),
            "zaman": time.time()
        })
        # Sadece son 5 metni tut
        if len(_son_vera_metinleri) > 5:
            _son_vera_metinleri.pop(0)


def _vera_metni_mi(algilanan: str) -> bool:
    """Algılanan metin Vera'nın kendi sesi mi kontrol et"""
    algilanan = algilanan.lower().strip()
    simdi = time.time()

    with _son_vera_kilidi:
        # Süresi dolmuş girişleri temizle
        gecerli = [m for m in _son_vera_metinleri
                   if simdi - m["zaman"] < _VERA_METIN_SURE]
        _son_vera_metinleri.clear()
        _son_vera_metinleri.extend(gecerli)

        for kayit in gecerli:
            vera_metin = kayit["metin"]
            kelimeler = algilanan.split()

            # 2 kelimeden kısa ise atla
            if len(kelimeler) < 2:
                continue

            # Yöntem 1: Kelime eşleşme oranı
            eslesen = sum(1 for k in kelimeler if k in vera_metin)
            oran = eslesen / len(kelimeler)
            if oran >= 0.45:
                print(f"[FİLTRE] Kelime oranı eşleşti ({oran:.0%}): {algilanan[:40]}")
                return True

            # Yöntem 2: Algılanan metin Vera metninin alt dizisi mi
            # 4+ kelimelik örtüşen ardışık dizi varsa filtrele
            vera_kelimeler = vera_metin.split()
            for i in range(len(kelimeler) - 3):
                parca = " ".join(kelimeler[i:i+4])
                if parca in vera_metin:
                    print(f"[FİLTRE] Alt dizi eşleşti: {parca}")
                    return True

    return False


def set_konusma_callback(fn):
    global _konusma_cb
    _konusma_cb = fn


def mikrofonu_durdur():
    global _mikrofon_aktif
    with _mikrofon_kilit:
        _mikrofon_aktif = False
        print("[MİK] MİKROFON DURDURULDU")


def mikrofonu_baslat():
    global _mikrofon_aktif
    with _mikrofon_kilit:
        _mikrofon_aktif = True
        print("[MİK] MİKROFON BAŞLATILDI")


def mikrofon_aktif_mi() -> bool:
    with _mikrofon_kilit:
        return _mikrofon_aktif


def is_konusuyor() -> bool:
    return _konusuyor


def _islak_mi(frame_data: bytes, rate: int = 16000) -> bool:
    """
    Frekans analizi ile ıslık tespiti.
    Islık: enerjinin büyük kısmı 2000 Hz üzerinde (dar band, tonal ses).
    Konuşma: enerji geniş banda yayılmış, özellikle 80-2000 Hz aralığında.
    """
    try:
        import numpy as np
        samples = np.frombuffer(frame_data, dtype=np.int16).astype(np.float32)
        rms = float(np.sqrt(np.mean(samples ** 2)))
        if rms < 200:
            return False

        fft_mag = np.abs(np.fft.rfft(samples))
        freqs = np.fft.rfftfreq(len(samples), 1.0 / rate)

        toplam = float(np.sum(fft_mag ** 2))
        if toplam < 1.0:
            return False

        # Islık bandı: 1200 Hz üzeri — insan ıslığı genelde 1000-4000 Hz
        yuksek = float(np.sum(fft_mag[freqs > 1200] ** 2))
        oran = yuksek / toplam

        # Yüksek frekanslarda enerji baskın VE yeterince güçlü → ıslık
        return oran > 0.60 and rms > 200
    except ImportError:
        import struct, math as _math
        s = struct.unpack(f"{len(frame_data)//2}h", frame_data)
        rms = _math.sqrt(sum(x*x for x in s) / len(s)) if s else 0
        return rms > 600
    except Exception:
        return False


def _tts_uret(metin: str):
    try:
        import edge_tts
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            tmp = f.name
        async def _gen():
            comm = edge_tts.Communicate(metin, EDGE_TTS_VOICE, rate="+25%")
            await comm.save(tmp)
        asyncio.run(_gen())
        return tmp
    except Exception as e:
        print(f"[TTS ÜRET] {e}")
        return None


def _tts_pyttsx3(metin: str) -> str | None:
    """İnternet gerektirmeyen offline TTS (Windows SAPI)."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)
        # Türkçe ses varsa seç
        voices = engine.getProperty('voices')
        for v in voices:
            vid = (v.id or "").lower()
            vname = (v.name or "").lower()
            if "turkish" in vname or "tr-tr" in vid or "tr_tr" in vid:
                engine.setProperty('voice', v.id)
                break
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp = f.name
        engine.save_to_file(metin, tmp)
        engine.runAndWait()
        if os.path.exists(tmp) and os.path.getsize(tmp) > 100:
            return tmp
        return None
    except Exception as e:
        print(f"[TTS PYTTSX3] {e}")
        return None


def tts_onbellek_doldur():
    on_bellek_listesi = [
        "Buradayım, dinliyorum.",
        "Evet, söyle.",
        "Dinliyorum.",
        "Buyur?",
        "Hazırım.",
        "Tamam, ışığı açtım.",
        "Işığı söndürdüm.",
        "Anlaşıldı.",
        "Görüşürüz!",
        "Rica ederim!",
        "Merhaba!",
        "İyiyim, teşekkürler!",
        "İşte Netflix, keyifle kullan!",
        "Netflix açılıyor.",
        "Chrome açılıyor.",
    ]

    def _doldur():
        for metin in on_bellek_listesi:
            if metin not in _tts_cache:
                yol = _tts_uret(metin)
                if yol:
                    _tts_cache[metin] = yol
        print(f"[TTS] Önbellek hazır: {len(_tts_cache)} yanıt")

    threading.Thread(target=_doldur, daemon=True).start()


def konus(metin: str, bitti_cb=None):
    global _konusuyor, _konusma_baslangic_zamani

    if _konusuyor:
        print("[SES] Zaten konuşuyor, yeni konuşma atlandı.")
        if bitti_cb:
            bitti_cb()
        return

    def _run():
        global _konusuyor, _konusma_baslangic_zamani

        mikrofonu_durdur()
        _konusuyor = True
        _konusma_baslangic_zamani = time.time()

        # Vera'nın söyleyeceği metni kaydet — mikrofon bu metni algılarsa filtrele
        _vera_metin_ekle(metin)

        if _konusma_cb:
            _konusma_cb(True)

        tmp = None
        onbellekten = False
        try:
            import pygame

            if metin in _tts_cache and os.path.exists(_tts_cache[metin]):
                tmp = _tts_cache[metin]
                onbellekten = True
            else:
                tmp = _tts_uret(metin)

            if tmp and os.path.exists(tmp):
                pygame.mixer.music.load(tmp)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    time.sleep(0.05)

                pygame.mixer.music.stop()
                pygame.mixer.music.unload()

                if onbellekten:
                    tmp = None
            else:
                raise Exception("TTS dosyası oluşturulamadı")

        except Exception as e:
            print(f"[SES] edge-tts hatası: {e}")
            sesli = False
            try:
                from gtts import gTTS
                tts = gTTS(text=metin, lang="tr", slow=False)
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    tmp = f.name
                tts.save(tmp)
                pygame.mixer.music.load(tmp)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.05)
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                sesli = True
            except Exception as e2:
                print(f"[SES] gTTS fallback hatası: {e2}")

            if not sesli:
                # Offline fallback: Windows SAPI (pyttsx3)
                try:
                    wav = _tts_pyttsx3(metin)
                    if wav and os.path.exists(wav):
                        pygame.mixer.music.load(wav)
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy():
                            time.sleep(0.05)
                        pygame.mixer.music.stop()
                        pygame.mixer.music.unload()
                        try:
                            os.unlink(wav)
                        except Exception:
                            pass
                except Exception as e3:
                    print(f"[SES] pyttsx3 fallback hatası: {e3}")
        finally:
            if tmp and not onbellekten and os.path.exists(tmp):
                try:
                    os.unlink(tmp)
                except Exception:
                    pass

            _konusuyor = False

            time.sleep(_KONUSMA_BEKLEME_SURESI)
            mikrofonu_baslat()

            if _konusma_cb:
                _konusma_cb(False)
            if bitti_cb:
                bitti_cb()

    threading.Thread(target=_run, daemon=True).start()


def dinle(on_komut, uyuyor_fn=lambda: True, on_ses_cb=None):
    """
    İki modlu dinleme:
    - Uyku modu  : 1.5s sliding window → STT → 'vera' ara (hızlı, VAD beklemez)
    - Uyanık modu: VAD tabanlı tam cümle algılama; ses geldiğinde on_ses_cb çağrılır
    """
    try:
        import pyaudio
        import struct
        import math
        import speech_recognition as sr

        RATE = 16000
        CHUNK = 480  # 30ms @ 16kHz

        def _rms(data):
            samples = struct.unpack(f"{len(data) // 2}h", data)
            return math.sqrt(sum(s * s for s in samples) / len(samples)) if samples else 0.0

        rec = sr.Recognizer()
        pa = pyaudio.PyAudio()
        stream = pa.open(
            rate=RATE, channels=1, format=pyaudio.paInt16,
            input=True, frames_per_buffer=CHUNK
        )

        # Kalibrasyon
        cal = [_rms(stream.read(CHUNK, exception_on_overflow=False)) for _ in range(30)]
        noise_floor = sum(cal) / len(cal)
        threshold = max(200.0, noise_floor * 2.5)
        print(f"[MİK] Gürültü={noise_floor:.0f}  Eşik={threshold:.0f}")

        # Uyku modu — frekans analizi ile ıslık tespiti
        # Islık: 1500 Hz üzeri enerjinin %60'ından fazlası → ıslık
        # Konuşma: enerji geniş banda dağılmış, yüksek-frek oranı düşük → yoksay
        son_islak_zamani = 0.0
        ISLAK_BEKLEME = 3.0
        _islak_sayac = 0
        ISLAK_MAX_FRAMES = 20  # 20 * 30ms = 600ms — max ıslık süresi
        print("[MİK] Islık tespiti: frekans analizi aktif")

        # Uyanık modu VAD
        SILENCE_FRAMES_NEEDED = 25  # 750ms sessizlik → cümle bitti (daha uzun dinle)
        MIN_SPEECH_FRAMES = 4
        MAX_FRAMES = 1000

        uyandirma_kelimeler = ["vera", "uyan", "hey vera", "heyver", "vera uyan"]
        kisa_komutlar = {
            "mavi", "kirmizi", "yesil", "sari", "mor", "pembe",
            "beyaz", "turkuaz", "amber", "mint", "fusya", "mercan",
            "limon", "okyanus", "eflatun", "seftali", "lavanta",
            "ac", "kapat", "yak", "sondur", "dur", "tamam", "evet", "hayir"
        }

        son_algilama_zamani = 0
        ALGILAMA_BEKLEME = 2.0

        try:
            while True:
                try:
                    frame = stream.read(CHUNK, exception_on_overflow=False)
                except Exception:
                    time.sleep(0.01)
                    continue

                # ════════════════════════════════════════════════════════
                # UYKU MODU — mikrofon kontrolünden önce çalışır
                # Vera konuşurken de ıslık tespiti aktif kalır
                # ════════════════════════════════════════════════════════
                if uyuyor_fn():
                    # Frekans analizi: ıslık = yüksek frekanslarda baskın enerji
                    suan = time.time()
                    if _islak_mi(frame):
                        _islak_sayac += 1
                        if _islak_sayac > ISLAK_MAX_FRAMES:
                            _islak_sayac = 0
                    else:
                        if 3 <= _islak_sayac <= ISLAK_MAX_FRAMES:
                            if suan - son_islak_zamani > ISLAK_BEKLEME:
                                son_islak_zamani = suan
                                print(f"[UYKU] Islık: {_islak_sayac*30}ms — tetiklendi")
                                on_komut("ıslık")
                        _islak_sayac = 0
                    continue

                if not mikrofon_aktif_mi():
                    continue

                e = _rms(frame)

                # ════════════════════════════════════════════════════════
                # UYANIK MOD — VAD tabanlı tam cümle algılama
                # ════════════════════════════════════════════════════════
                noise_floor = 0.005 * e + 0.995 * noise_floor
                threshold = max(200.0, noise_floor * 2.5)

                # Ses aktivitesi → uyku sayacını sıfırla
                if on_ses_cb and e > threshold * 0.6:
                    on_ses_cb()

                if e <= threshold:
                    continue

                # Konuşma başladı → kayıt başlat
                frames = [frame]
                speech_frame_count = 1
                silence_frame_count = 0

                while True:
                    try:
                        frame = stream.read(CHUNK, exception_on_overflow=False)
                    except Exception:
                        time.sleep(0.01)
                        continue

                    if not mikrofon_aktif_mi():
                        frames = []
                        break

                    frames.append(frame)
                    e = _rms(frame)

                    if e > threshold * 0.4:
                        speech_frame_count += 1
                        silence_frame_count = 0
                    else:
                        silence_frame_count += 1

                    if silence_frame_count >= SILENCE_FRAMES_NEEDED:
                        break
                    if len(frames) >= MAX_FRAMES:
                        break

                if not frames or speech_frame_count < MIN_SPEECH_FRAMES:
                    continue

                audio_bytes = b"".join(frames)
                audio = sr.AudioData(audio_bytes, RATE, 2)

                try:
                    metin = rec.recognize_google(audio, language="tr-TR")
                    if not metin.strip():
                        continue

                    metin_lower = metin.lower().strip()

                    if any(k in metin_lower for k in uyandirma_kelimeler):
                        print(f"[MİK] Uyandırma: {metin}")
                        on_komut(metin)
                        continue

                    if len(metin.strip()) < 5:
                        if not any(k in metin_lower for k in kisa_komutlar):
                            print(f"[MİK] Çok kısa, yok sayıldı: {metin}")
                            continue

                    if _vera_metni_mi(metin):
                        print(f"[FİLTRE] Vera'nın kendi sesi: {metin[:50]}")
                        continue

                    suan = time.time()
                    if suan - son_algilama_zamani < ALGILAMA_BEKLEME:
                        print(f"[MİK] Çok hızlı tekrar, yok sayıldı.")
                        continue

                    son_algilama_zamani = suan
                    print(f"[MİK] Algılandı: {metin}")
                    on_komut(metin)

                except sr.UnknownValueError:
                    pass
                except sr.RequestError as ex:
                    print(f"[STT] {ex}")
                    time.sleep(2)

        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()

    except Exception as e:
        print(f"[MİK] {e}")
