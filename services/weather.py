# ══════════════════════════════════════════════════════════════
# HAVA DURUMU
# ══════════════════════════════════════════════════════════════

import requests
from core.config import CITIES, WEATHER_KEY, HAVA_TR


def hava_durumu(sehir_n: str) -> str:
    """Belirtilen şehrin hava durumunu getirir."""
    if sehir_n not in CITIES:
        return "Bu şehri bilmiyorum. Bursa, İstanbul, Ankara veya İzmir diyebilirsin."
    try:
        c = CITIES[sehir_n]
        url = (
            f"https://api.openweathermap.org/data/2.5/forecast"
            f"?lat={c['lat']}&lon={c['lon']}"
            f"&appid={WEATHER_KEY}&units=metric&cnt=8"
        )
        r = requests.get(url, timeout=6)
        data = r.json()
        if r.status_code != 200:
            return f"Hava durumu alınamadı: {data.get('message', 'hata')}"

        now = data["list"][0]
        sicak = round(now["main"]["temp"])
        hiss = round(now["main"]["feels_like"])
        nem = now["main"]["humidity"]
        ruzgar = round(now["wind"]["speed"] * 3.6)
        desc = now["weather"][0]["description"]
        durum = HAVA_TR.get(desc, desc)
        pop_max = round(max(x.get("pop", 0) for x in data["list"][:4]) * 100)

        if pop_max >= 70:
            yagmur_yorum = f"Yağmur ihtimali yüzde {pop_max}. Şemsiyeni almayı unutma."
        elif pop_max >= 40:
            yagmur_yorum = f"Yağmur ihtimali yüzde {pop_max}, dikkatli ol."
        elif pop_max >= 15:
            yagmur_yorum = f"Yağmur ihtimali yüzde {pop_max}."
        else:
            yagmur_yorum = "Yağmur beklenmez."

        if ruzgar >= 50:
            ruzgar_yorum = f"Rüzgar oldukça sert, saatte {ruzgar} kilometre."
        elif ruzgar >= 25:
            ruzgar_yorum = f"Orta kuvvette rüzgar var, saatte {ruzgar} kilometre."
        else:
            ruzgar_yorum = f"Rüzgar sakin, saatte {ruzgar} kilometre."

        goster = c["goster"]
        return (
            f"{goster} şu an {durum}. "
            f"Sıcaklık {sicak} derece, hissedilen {hiss} derece. "
            f"Nem yüzde {nem} "
            f"{ruzgar_yorum} "
            f"{yagmur_yorum}"
        )
    except Exception as e:
        return f"Hava durumu alınamadı: {e}"