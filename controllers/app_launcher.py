# ══════════════════════════════════════════════════════════════
# UYGULAMA AÇMA
# ══════════════════════════════════════════════════════════════

import time
import threading
import random
import pyautogui


def uygulama_ac(goster: str) -> str:
    """Belirtilen uygulamayı açar."""
    def _ara():
        time.sleep(0.3)
        try:
            pyautogui.hotkey("win", "s")
            time.sleep(0.6)
            pyautogui.write(goster, interval=0.04)
            time.sleep(0.8)
            pyautogui.press("enter")
        except Exception as e:
            print(f"[UYGULAMA AÇ] {e}")

    threading.Thread(target=_ara, daemon=True).start()

    return random.choice([
        f"Hemen açıyorum, {goster} geliyor!",
        f"Tamam, {goster} açılıyor.",
        f"{goster} şimdi açılıyor, bir saniye.",
        f"Anlaşıldı, {goster} başlatılıyor.",
        f"{goster} hemen geliyor, bekle.",
        f"İşte {goster}, keyifle kullan!",
    ])