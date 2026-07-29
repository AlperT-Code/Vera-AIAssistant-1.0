import requests
import base64
import json
import os
import subprocess
import webbrowser
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from core.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

# Global degiskenler
_spotify_token = None
_spotify_refresh_token = None
_device_id = None
_authorization_code = None

# Token dosyasi yolu (script ile ayni klasorde gizli dosya)
TOKEN_FILE = os.path.join(os.path.dirname(__file__), ".spotify_token.json")


# ═══════════════════════════════════════════════
# TOKEN KAYIT / YUKLE
# ═══════════════════════════════════════════════

def _token_kaydet():
    """Token'lari diske kaydet"""
    try:
        with open(TOKEN_FILE, "w") as f:
            json.dump({
                "access_token": _spotify_token,
                "refresh_token": _spotify_refresh_token
            }, f)
    except Exception as e:
        print(f"[SPOTIFY] Token kaydedilemedi: {e}")


def _token_yukle():
    """Daha once kaydedilmis token'lari yukle"""
    global _spotify_token, _spotify_refresh_token
    try:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "r") as f:
                data = json.load(f)
                _spotify_token = data.get("access_token")
                _spotify_refresh_token = data.get("refresh_token")
                print("[SPOTIFY] Token dosyadan yuklendi.")
                return True
    except Exception as e:
        print(f"[SPOTIFY] Token yuklenemedi: {e}")
    return False


# Modul yuklenince token'lari hemen yukle
_token_yukle()


# ═══════════════════════════════════════════════
# AUTH SUNUCUSU
# ═══════════════════════════════════════════════

class SpotifyAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global _authorization_code
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if "code" in params:
            _authorization_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            # Sayfa acilir acilmaz kendini kapatir
            self.wfile.write(
                b"<html><head>"
                b"<script>window.onload=function(){window.close();}</script>"
                b"</head><body></body></html>"
            )
        else:
            self.send_response(400)
            self.end_headers()

    def log_message(self, format, *args):
        # Sunucu loglarini bastir
        pass


# ═══════════════════════════════════════════════
# TOKEN AL / YENILE
# ═══════════════════════════════════════════════

def get_spotify_token():
    """Spotify access token al — once cache, sonra refresh, son care yeni auth"""
    global _spotify_token, _spotify_refresh_token, _authorization_code

    # 1. Refresh token varsa yenile
    if _spotify_refresh_token:
        try:
            auth_string = base64.b64encode(
                f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode("utf-8")
            ).decode()

            response = requests.post(
                "https://accounts.spotify.com/api/token",
                headers={
                    "Authorization": f"Basic {auth_string}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": _spotify_refresh_token,
                },
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                _spotify_token = data.get("access_token")
                if "refresh_token" in data:
                    _spotify_refresh_token = data.get("refresh_token")
                _token_kaydet()
                return _spotify_token
            else:
                print(f"[SPOTIFY] Refresh basarisiz ({response.status_code}), yeni auth gerekiyor.")
                _spotify_refresh_token = None

        except Exception as e:
            print(f"[SPOTIFY] Refresh hatasi: {e}")

    # 2. Yeni auth akisi
    try:
        _authorization_code = None

        # Auth sunucusunu baslat
        server = HTTPServer(("localhost", 8888), SpotifyAuthHandler)
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()

        # Auth URL'i ac
        auth_url = (
            f"https://accounts.spotify.com/authorize?"
            f"client_id={SPOTIFY_CLIENT_ID}&"
            f"response_type=code&"
            f"redirect_uri={SPOTIFY_REDIRECT_URI}&"
            f"scope=user-read-playback-state%20user-modify-playback-state%20"
            f"user-read-currently-playing%20app-remote-control%20streaming%20"
            f"playlist-read-private%20playlist-read-collaborative%20"
            f"playlist-modify-public%20playlist-modify-private"
        )

        print("[SPOTIFY] Tarayici ile Spotify girisi yapiliyor...")
        webbrowser.open(auth_url)

        # Kod gelene kadar bekle (max 120 saniye)
        timeout = 120
        start = time.time()
        while _authorization_code is None and (time.time() - start) < timeout:
            time.sleep(0.5)

        server.shutdown()

        if _authorization_code is None:
            print("[SPOTIFY] Auth zaman asimina ugradi.")
            return None

        # Kodu token ile degistir
        auth_string = base64.b64encode(
            f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode("utf-8")
        ).decode()

        response = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": f"Basic {auth_string}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "authorization_code",
                "code": _authorization_code,
                "redirect_uri": SPOTIFY_REDIRECT_URI,
            },
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            _spotify_token = data.get("access_token")
            _spotify_refresh_token = data.get("refresh_token")
            _token_kaydet()
            print("[SPOTIFY] Yeni token alindi ve kaydedildi.")
            return _spotify_token
        else:
            print(f"[SPOTIFY] Token hatasi: {response.text}")
            return None

    except Exception as e:
        print(f"[SPOTIFY] Auth hatasi: {e}")
        return None


def spotify_headers():
    """Spotify API istekleri icin header"""
    token = get_spotify_token()
    if not token:
        return None
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


# ═══════════════════════════════════════════════
# CIHAZ BULMA
# ═══════════════════════════════════════════════

def get_spotify_device():
    """Kullanilabilir Spotify cihazini bul"""
    global _device_id

    headers = spotify_headers()
    if not headers:
        return None

    try:
        response = requests.get(
            "https://api.spotify.com/v1/me/player/devices",
            headers=headers,
            timeout=10,
        )

        if response.status_code == 200:
            devices = response.json().get("devices", [])
            if not devices:
                print("[SPOTIFY] Hic cihaz bulunamadi. Spotify acik mi?")
                return None

            # Once aktif cihaz
            for device in devices:
                if device.get("is_active"):
                    _device_id = device.get("id")
                    return _device_id

            # Sonra bilgisayar tipi
            for device in devices:
                dtype = device.get("type", "").lower()
                dname = device.get("name", "").lower()
                if "computer" in dtype or "pc" in dname:
                    _device_id = device.get("id")
                    return _device_id

            # Herhangi biri
            _device_id = devices[0].get("id")
            return _device_id

        print(f"[SPOTIFY] Cihaz hatasi: {response.status_code} {response.text}")
        return None

    except Exception as e:
        print(f"[SPOTIFY] Cihaz hatasi: {e}")
        return None


# ═══════════════════════════════════════════════
# SARKI CAL
# ═══════════════════════════════════════════════

def _spotify_uygulamasi_baslat():
    """Spotify uygulamasını arka planda başlatır."""
    try:
        subprocess.Popen("start spotify:", shell=True)
        return True
    except Exception as e:
        print(f"[SPOTIFY] Uygulama başlatılamadı: {e}")
        return False


def spotify_uygulamasi_ac() -> str:
    """Spotify uygulamasını açar."""
    if _spotify_uygulamasi_baslat():
        return "Spotify açılıyor."
    return "Spotify açılamadı."


def spotify_sarki_ac(sarki_adi: str) -> str:
    """Spotify'da sarki ara ve cal; gerekirse uygulamayi once ac."""
    try:
        headers = spotify_headers()
        if not headers:
            return "Spotify oturumu acilamadi. Lutfen tekrar dener misin?"

        # Sarki ara — 5 sonuc al, Turkiye pazarini onceliklendir
        response = requests.get(
            "https://api.spotify.com/v1/search",
            headers=headers,
            params={
                "q": sarki_adi,
                "type": "track",
                "limit": 5,
                "market": "TR",
            },
            timeout=10,
        )

        if response.status_code != 200:
            print(f"[SPOTIFY] Arama hatasi: {response.status_code} {response.text}")
            return "Sarki aranirken bir hata olustu."

        data = response.json()
        tracks = data.get("tracks", {}).get("items", [])

        if not tracks:
            return f"'{sarki_adi}' adli sarki bulunamadi."

        # En iyi eslesmeyi al
        track = tracks[0]
        track_id = track["id"]
        track_name = track["name"]
        artists = ", ".join([artist["name"] for artist in track["artists"]])

        # Cihaz bul; yoksa Spotify'ı aç ve tekrar dene
        device_id = get_spotify_device()
        if not device_id:
            print("[SPOTIFY] Cihaz bulunamadı, Spotify açılıyor...")
            _spotify_uygulamasi_baslat()
            for _ in range(15):
                time.sleep(1)
                device_id = get_spotify_device()
                if device_id:
                    break

        if not device_id:
            return "Spotify açıldı ama cihaz henüz hazır değil. Birkaç saniye bekleyip tekrar dener misin?"

        # Cal
        response = requests.put(
            f"https://api.spotify.com/v1/me/player/play?device_id={device_id}",
            headers=headers,
            json={
                "uris": [f"spotify:track:{track_id}"],
                "offset": {"position": 0},
                "position_ms": 0,
            },
            timeout=10,
        )

        if response.status_code in [200, 204]:
            return f"'{track_name}' - {artists} çalıyor."
        elif response.status_code == 404:
            return "Spotify uygulamasi bulunamadi. Spotify'i acar misin?"
        elif response.status_code == 403:
            return "Bu islemi yapmak icin Spotify Premium gerekiyor."
        else:
            print(f"[SPOTIFY] Calma hatasi: {response.status_code} {response.text}")
            return "Sarki calinamadi."

    except Exception as e:
        print(f"[SPOTIFY] Sarki ac hatasi: {e}")
        return "Sarki calinirken bir hata olustu."


# ═══════════════════════════════════════════════
# SIMDI NE CALIYOR
# ═══════════════════════════════════════════════

def spotify_calani_ogren() -> str:
    """Simdi calani ogren"""
    headers = spotify_headers()
    if not headers:
        return "Spotify oturumu acilamadi."

    try:
        response = requests.get(
            "https://api.spotify.com/v1/me/player/currently-playing",
            headers=headers,
            timeout=10,
        )

        if response.status_code == 204:
            return "Simdi hicbir sey calmiyor."

        if response.status_code == 200:
            data = response.json()
            if data and data.get("item"):
                track = data["item"]
                name = track["name"]
                artists = ", ".join([artist["name"] for artist in track["artists"]])
                progress = data.get("progress_ms", 0) // 1000
                duration = track.get("duration_ms", 0) // 1000
                durum = "caliyor" if data.get("is_playing") else "durdurulmus"
                return (
                    f"{name} - {artists} {durum}. "
                    f"{progress // 60}:{progress % 60:02d} / "
                    f"{duration // 60}:{duration % 60:02d}"
                )
            return "Simdi hicbir sey calmiyor."

        print(f"[SPOTIFY] Calani ogrenme hatasi: {response.status_code}")
        return "Spotify bilgisi alinamadi."

    except Exception as e:
        print(f"[SPOTIFY] Calani ogrenme hatasi: {e}")
        return "Bir hata olustu."


# ═══════════════════════════════════════════════
# DURDUR / DEVAM
# ═══════════════════════════════════════════════

def spotify_durdur() -> str:
    """Calmayi durdur"""
    headers = spotify_headers()
    if not headers:
        return "Spotify oturumu acilamadi."

    try:
        response = requests.put(
            "https://api.spotify.com/v1/me/player/pause",
            headers=headers,
            timeout=10,
        )

        if response.status_code in [200, 204]:
            return "Müzik durduruldu."
        elif response.status_code == 403:
            return "Spotify Premium gerekiyor."
        return "Müzik durdurulamadi."

    except Exception as e:
        print(f"[SPOTIFY] Durdurma hatasi: {e}")
        return "Bir hata olustu."


def spotify_cal() -> str:
    """Calmayi devam ettir"""
    headers = spotify_headers()
    if not headers:
        return "Spotify oturumu acilamadi."

    device_id = get_spotify_device()
    if not device_id:
        return "Spotify cihazi bulunamadi."

    try:
        response = requests.put(
            f"https://api.spotify.com/v1/me/player/play?device_id={device_id}",
            headers=headers,
            timeout=10,
        )

        if response.status_code in [200, 204]:
            return "Müzik devam ediyor."
        elif response.status_code == 403:
            return "Spotify Premium gerekiyor."
        return "Müzik devam ettirilemedi."

    except Exception as e:
        print(f"[SPOTIFY] Devam hatasi: {e}")
        return "Bir hata olustu."


# ═══════════════════════════════════════════════
# SES KONTROLU
# ═══════════════════════════════════════════════

def spotify_ses_ac(kapat: bool) -> str:
    """Sesi kapat (True) veya ac (False)"""
    headers = spotify_headers()
    if not headers:
        return "Spotify oturumu acilamadi."

    volume = 0 if kapat else 100

    try:
        response = requests.put(
            f"https://api.spotify.com/v1/me/player/volume?volume_percent={volume}",
            headers=headers,
            timeout=10,
        )

        if response.status_code in [200, 204]:
            return "Ses kapatildi." if kapat else "Ses acildi."
        elif response.status_code == 403:
            return "Spotify Premium gerekiyor."
        return "Ses ayarlanamadi."

    except Exception as e:
        print(f"[SPOTIFY] Ses hatasi: {e}")
        return "Bir hata olustu."