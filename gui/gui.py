import threading
import time
import math
import random
import tkinter as tk
from core.commands import komut_isle, vera_uyan, vera_uyu

_DEVAM_SORULARI = [
    "Başka?",
    "Başka bir şey?",
    "Başka isteğin?",
    "Ne daha?",
    "Bir şey daha?",
    "Başka ne var?",
    "Daha ne istersin?",
    "Yardımcı olabileceğim başka bir şey?",
]
from services.speech import (set_konusma_callback, konus, dinle, tts_onbellek_doldur,
                    mikrofon_aktif_mi, _spotify_duck, _spotify_unduck)
from core.database import sohbet_kaydet
from core.config import EDGE_TTS_VOICE


WIN_W, WIN_H = 460, 580
CX, CY = WIN_W // 2, 225
R_BASE = 120


class AsistanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Vera - Sesli Asistan")
        self.root.configure(bg="#F5F5F0")
        self.root.geometry(f"{WIN_W}x{WIN_H}")
        self.root.resizable(False, False)

        self.konusuyor = False
        self.uyuyor = False
        self.arkada_bekliyor = False
        self.r_cur = float(R_BASE)
        self.r_tgt = float(R_BASE)
        self._komut_kilidi = threading.Lock()
        self._komut_beklemede = False
        self._son_komut_zamani = 0
        self._son_aktif_zaman = time.time()

        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

        self._build()
        self._start()
        self._animate()

    def _uyku_gir(self):
        self.uyuyor = True
        self._ui(durum="Uyuyor...", drenk="#BBBBBB")
        threading.Thread(target=_spotify_unduck, daemon=True).start()

    def _uyku_cik(self):
        self.uyuyor = False
        self._son_aktif_zaman = time.time()
        self._ui(durum="Dinleniyor...", drenk="#888888")
        threading.Thread(target=_spotify_duck, daemon=True).start()

    def _arkaplan_gir(self):
        self.arkada_bekliyor = True
        def _gizle():
            self.root.after(0, self.root.withdraw)
        konus("Arkada bekliyorum.", bitti_cb=_gizle)

    def _arkaplan_cik(self):
        self.arkada_bekliyor = False
        self.root.after(0, self.root.deiconify)
        if self.uyuyor:
            self._uyku_cik()
        else:
            self._son_aktif_zaman = time.time()
            self._ui(durum="Dinleniyor...", drenk="#888888")
        yanit = vera_uyan()
        konus(yanit)

    def _build(self):
        tk.Label(
            self.root, text="VERA",
            font=("Courier New", 14, "bold"),
            bg="#F5F5F0", fg="#111111"
        ).pack(pady=(20, 0))

        self.cv = tk.Canvas(
            self.root, width=WIN_W, height=WIN_H - 185,
            bg="#F5F5F0", highlightthickness=0
        )
        self.cv.pack()

        bottom = tk.Frame(self.root, bg="#F5F5F0")
        bottom.pack(fill="x", padx=28, pady=(0, 14))

        self.lbl_durum = tk.Label(
            bottom, text="Dinleniyor...",
            font=("Courier New", 9),
            bg="#F5F5F0", fg="#888888"
        )
        self.lbl_durum.pack()

        self.lbl_metin = tk.Label(
            bottom, text="",
            font=("Georgia", 10, "italic"),
            bg="#F5F5F0", fg="#444444",
            wraplength=410, justify="center"
        )
        self.lbl_metin.pack(pady=(5, 0))

        self.lbl_yanit = tk.Label(
            bottom, text="",
            font=("Courier New", 9),
            bg="#F5F5F0", fg="#111111",
            wraplength=410, justify="center"
        )
        self.lbl_yanit.pack(pady=(4, 0))

    def _ui(self, metin=None, yanit=None, durum=None, drenk="#888888"):
        def _do():
            if metin is not None:
                self.lbl_metin.config(text=f'"{metin}"')
            if yanit is not None:
                self.lbl_yanit.config(text="")
            if durum is not None:
                self.lbl_durum.config(text=durum, fg=drenk)
        self.root.after(0, _do)

    def _animate(self):
        try:
            self.cv.delete("all")
            t = time.time()
            uyuyor = self.uyuyor

            # Uyanıkken 20s komut gelmezse otomatik uyu
            if not uyuyor and not self.konusuyor and self._son_aktif_zaman > 0:
                if t - self._son_aktif_zaman > 20:
                    self._uyku_gir()
                    uyuyor = True

            if uyuyor:
                self.r_tgt = R_BASE * 0.78 + 4 * math.sin(t * 0.38)
            elif self.konusuyor:
                self.r_tgt = R_BASE + 20 * math.sin(t * 8)
            else:
                self.r_tgt = R_BASE + 5 * math.sin(t * 1.3)

            self.r_cur += (self.r_tgt - self.r_cur) * 0.15
            r = self.r_cur

            n = 200
            pts_out, pts_in = [], []
            for i in range(n):
                a = 2 * math.pi * i / n
                if uyuyor:
                    w = (3 * math.sin(3 * a + t * 0.35) +
                         2 * math.sin(6 * a - t * 0.25))
                elif self.konusuyor:
                    w = (16 * math.sin(5 * a + t * 9) +
                         9 * math.sin(9 * a - t * 7) +
                         5 * math.sin(15 * a + t * 5))
                else:
                    w = (6 * math.sin(4 * a + t * 1.5) +
                         3 * math.sin(8 * a - t * 2) +
                         2 * math.sin(13 * a + t))
                rr = r + w
                ri = max(rr - 15, 18)
                pts_out.extend([CX + rr * math.cos(a), CY + rr * math.sin(a)])
                pts_in.extend([CX + ri * math.cos(a), CY + ri * math.sin(a)])

            if uyuyor:
                sh_col, fill_col, in_col, v_col = "#E8E8E8", "#CCCCCC", "#F2F2F2", "#AAAAAA"
            else:
                sh_col, fill_col, in_col, v_col = "#E0E0E0", "#111111", "#FFFFFF", "#111111"

            sh = [v + 4 for v in pts_out]
            self.cv.create_polygon(sh,      fill=sh_col,   outline="", smooth=True)
            self.cv.create_polygon(pts_out, fill=fill_col, outline="", smooth=True)
            self.cv.create_polygon(pts_in,  fill=in_col,   outline="", smooth=True)

            fs = max(16, int(r * 0.52))
            self.cv.create_text(CX, CY + 3, text="V",
                                font=("Georgia", fs, "bold"), fill=v_col)

            if uyuyor:
                # 4 Z: üst-sağ çaprazında, ~27px aralıklı
                z_period = 4.0
                z_configs = [
                    # (x_base, y_start, zaman_ofseti, temel_boyut)
                    (CX + 98, CY - 52, 0.00, 30),
                    (CX + 106, CY - 78, 1.00, 23),
                    (CX + 112, CY - 104, 2.00, 17),
                    (CX + 115, CY - 130, 3.00, 12),
                ]
                for zx, zy, t_off, bsize in z_configs:
                    prog = ((t + t_off) % z_period) / z_period
                    if prog < 0.22:
                        alpha_v = prog / 0.22
                    else:
                        alpha_v = 1.0 - (prog - 0.22) / 0.78
                    if alpha_v < 0.05:
                        continue
                    x = zx + prog * 8
                    y = zy - prog * 38
                    gray  = int(210 - alpha_v * 165)
                    color = f"#{gray:02x}{gray:02x}{gray:02x}"
                    fsize = max(7, int(bsize * (0.45 + 0.55 * alpha_v)))
                    self.cv.create_text(int(x), int(y), text="Z",
                                        font=("Georgia", fsize, "bold italic"),
                                        fill=color)
        except Exception:
            pass

        try:
            self.root.after(28, self._animate)
        except Exception:
            pass

    def _start(self):
        set_konusma_callback(lambda b: (
            setattr(self, "konusuyor", b),
            self._ui(
                durum="Konuşuyor..." if b else (
                    "Uyuyor..." if self.uyuyor else "Dinleniyor..."),
                drenk="#222222" if b else (
                    "#BBBBBB" if self.uyuyor else "#888888")
            )
        ))

        def on_komut(metin):
            m_n = metin.lower()

            # ═══════════════════════════════════════════════
            # 1. ARKA PLAN ÇIKIŞ - ISLAK + ARK PLANDA BEKLİYOR
            # ═══════════════════════════════════════════════

            if "ıslık" in m_n and self.arkada_bekliyor:
                self._arkaplan_cik()
                return

            # ═══════════════════════════════════════════════
            # 2. UYANDIRMA KONTROLÜ - HER ZAMAN ÇALIŞIR
            # ═══════════════════════════════════════════════

            uyandirma = any(k in m_n for k in [
                "vera", "uyan", "uyanik ol", "dinle beni",
                "hey vera", "hey ver", "heyver", "vera uyan", "uyan vera",
                "ıslık"
            ])

            if uyandirma:
                self._uyku_cik()
                yanit = vera_uyan()
                konus(yanit)
                return

            # ═══════════════════════════════════════════════
            # 2. UYKU MODUNDA - HİÇBİR KOMUT ÇALIŞMAZ
            # ═══════════════════════════════════════════════

            if self.uyuyor:
                print(f"[UYKU] Görmezden gelindi: {metin}")
                return

            # ═══════════════════════════════════════════════
            # 2b. ARKA PLAN BEKLEME TETİKLEYİCİ
            # ═══════════════════════════════════════════════

            arkada_bekle_tetik = any(k in m_n for k in [
                "arkada bekle", "arka planda bekle", "arka planda dur",
            ])
            if arkada_bekle_tetik:
                self._arkaplan_gir()
                return

            # ═══════════════════════════════════════════════
            # 2c. UYKU TETİKLEYİCİ
            # ═══════════════════════════════════════════════

            uyku_tetik = any(k in m_n for k in [
                "görüşürüz", "bay bay", "hoşça kal", "güle güle",
                "bye bye", "gidebilirsin", "git artık", "tamam git",
                "uyu artık", "dinlen artık", "kenara çekil",
                "artık git", "istirahat et", "tamam bye", "tamam bb"
            ])
            if uyku_tetik:
                yanit = vera_uyu()
                konus(yanit, bitti_cb=self._uyku_gir)
                return

            # ═══════════════════════════════════════════════
            # 3. KENDİ SESİNİ FİLTRELE
            # ═══════════════════════════════════════════════

            kendi_ses_patterns = [
                "işte netflix", "keyifle kullan", "açılıyor", "kapatılıyor",
                "ayarlandı", "anlaşıldı", "başlatılıyor", "söndürdüm",
                "açtım", "yaptım", "kapattım", "dinliyorum", "buyur",
                "hazırım", "evet söyle", "tamam", "oldu", "peki",
                "rica ederim", "iyi günler", "iyi akşamlar", "iyi geceler",
                "günaydın", "merhaba", "selam", "nasılsın", "iyiyim",
                "buradayım", "ne demek", "seve seve", "estağfurullah"
            ]

            metin_lower = metin.lower()
            for pattern in kendi_ses_patterns:
                if pattern in metin_lower:
                    if metin_lower.strip() == pattern or metin_lower.strip().startswith(pattern):
                        print(f"[FİLTRE] Asistan sesi filtrelendi: {metin}")
                        return

            # ═══════════════════════════════════════════════
            # 4. ANLAMSIZ KELİMELERİ FİLTRELE
            # ═══════════════════════════════════════════════

            anlamsiz_kelimeler = ["şey", "yani", "işte", "hmm", "aa", "eee", "ıı"]
            kelimeler = m_n.split()

            if kelimeler and all(k in anlamsiz_kelimeler for k in kelimeler):
                print(f"[FİLTRE] Anlamsız kelimeler filtrelendi: {metin}")
                return

            # ═══════════════════════════════════════════════
            # 5. ÇOK KISA KOMUTLARI FİLTRELE
            # ═══════════════════════════════════════════════

            if len(kelimeler) <= 2:
                tek_kelime_filtre = ["tamam", "evet", "hayır", "peki", "oldu",
                                     "tam", "yap", "et", "gel", "git", "dur"]
                if all(k in tek_kelime_filtre for k in kelimeler):
                    print(f"[FİLTRE] Tek kelime filtrelendi: {metin}")
                    return

            # ═══════════════════════════════════════════════
            # 6. MİKROFON KONTROLÜ
            # ═══════════════════════════════════════════════

            if not mikrofon_aktif_mi():
                print(f"[MİK] Mikrofon pasif, komut yok sayıldı: {metin}")
                return

            # ═══════════════════════════════════════════════
            # 7. ÇOK HIZLI TEKRAR ENGELLEME
            # ═══════════════════════════════════════════════

            if self._komut_beklemede:
                print(f"[KOMUT] Zaten işleniyor: {metin}")
                return

            suan = time.time()
            if suan - self._son_komut_zamani < 1.5:
                print(f"[KOMUT] Çok hızlı tekrar, yok sayıldı: {metin}")
                return

            # ═══════════════════════════════════════════════
            # 8. KOMUT İŞLE
            # ═══════════════════════════════════════════════

            if not self._komut_kilidi.acquire(blocking=False):
                print(f"[KOMUT] Meşgul, atlandı: {metin}")
                return

            self._komut_beklemede = True
            self._son_komut_zamani = suan

            def _isle():
                try:
                    print(f"Mic: {metin}")
                    self._ui(metin=metin, durum="Düşünüyor...", drenk="#444444")

                    yanit = komut_isle(metin)

                    if yanit is None:
                        self._komut_kilidi.release()
                        self._komut_beklemede = False
                        return

                    print(f"Vera: {yanit}")
                    # Konuşmayı arka planda DB'ye kaydet
                    threading.Thread(
                        target=sohbet_kaydet, args=(metin, yanit), daemon=True
                    ).start()

                    self._ui(durum="Konuşuyor...", drenk="#111111")

                    devam = random.choice(_DEVAM_SORULARI)
                    yanit_tam = yanit.rstrip(" .!?") + ". " + devam

                    def _bitti():
                        self._komut_kilidi.release()
                        self._komut_beklemede = False
                        # Uyumak yerine timer'ı sıfırla — 20s otomatik uyku devam eder
                        self._son_aktif_zaman = time.time()

                    konus(yanit_tam, bitti_cb=_bitti)

                except Exception as e:
                    print(f"[KOMUT HATA] {e}")
                    self._komut_kilidi.release()
                    self._komut_beklemede = False
                    self._son_aktif_zaman = time.time()

            threading.Thread(target=_isle, daemon=True).start()

        threading.Thread(
            target=lambda: dinle(
                on_komut,
                lambda: self.uyuyor or self.arkada_bekliyor,
                None
            ),
            daemon=True
        ).start()
        tts_onbellek_doldur()
        print("Vera hazır — dinleniyor.")
        print(f"   Ses: edge-tts ({EDGE_TTS_VOICE})")
