import os
from dotenv import load_dotenv

load_dotenv()

# ══════════════════════════════════════════════════════════════
# TÜM AYARLAR VE SABİTLER
# ══════════════════════════════════════════════════════════════

# API Anahtarları
WEATHER_KEY = os.getenv("WEATHER_KEY", "")

# Groq - Genel Sohbet / Yapay Zeka (Ücretsiz, Hızlı, Türkçe Mükemmel)
OPENROUTER_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENROUTER_MODEL = "llama-3.3-70b-versatile"
OPENROUTER_URL = "https://api.groq.com/openai/v1/chat/completions"

# Tuya Ampul Bilgileri
BULB_DEVICE_ID = os.getenv("BULB_DEVICE_ID", "")
BULB_LOCAL_KEY = os.getenv("BULB_LOCAL_KEY", "")
BULB_IP = os.getenv("BULB_IP", "")

# Ses Ayarları
EDGE_TTS_VOICE = "tr-TR-EmelNeural"

# Spotify API
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback")

# Şehir Bilgileri
# ══════════════════════════════════════════════════════════════
# CITIES — Tüm Türkiye illeri + büyük şehir ilçeleri
# ══════════════════════════════════════════════════════════════

CITIES = {
    # ── İSTANBUL (merkez + ilçeler) ───────────────────────────
    "istanbul":         {"lat": 41.0082, "lon": 28.9784, "goster": "İstanbul"},
    "adalar":           {"lat": 40.8739, "lon": 29.0908, "goster": "Adalar"},
    "arnavutköy":       {"lat": 41.1847, "lon": 28.7390, "goster": "Arnavutköy"},
    "ataşehir":         {"lat": 40.9923, "lon": 29.1244, "goster": "Ataşehir"},
    "avcılar":          {"lat": 40.9796, "lon": 28.7217, "goster": "Avcılar"},
    "bağcılar":         {"lat": 41.0390, "lon": 28.8560, "goster": "Bağcılar"},
    "bahçelievler":     {"lat": 41.0005, "lon": 28.8568, "goster": "Bahçelievler"},
    "bakırköy":         {"lat": 40.9793, "lon": 28.8724, "goster": "Bakırköy"},
    "başakşehir":       {"lat": 41.0928, "lon": 28.8019, "goster": "Başakşehir"},
    "bayrampaşa":       {"lat": 41.0453, "lon": 28.9133, "goster": "Bayrampaşa"},
    "beşiktaş":         {"lat": 41.0422, "lon": 29.0067, "goster": "Beşiktaş"},
    "beykoz":           {"lat": 41.1324, "lon": 29.1020, "goster": "Beykoz"},
    "beylikdüzü":       {"lat": 41.0008, "lon": 28.6400, "goster": "Beylikdüzü"},
    "beyoğlu":          {"lat": 41.0338, "lon": 28.9774, "goster": "Beyoğlu"},
    "büyükçekmece":     {"lat": 41.0186, "lon": 28.5856, "goster": "Büyükçekmece"},
    "çatalca":          {"lat": 41.1435, "lon": 28.4614, "goster": "Çatalca"},
    "çekmeköy":         {"lat": 41.0394, "lon": 29.1944, "goster": "Çekmeköy"},
    "esenler":          {"lat": 41.0436, "lon": 28.8762, "goster": "Esenler"},
    "esenyurt":         {"lat": 41.0378, "lon": 28.6726, "goster": "Esenyurt"},
    "eyüpsultan":       {"lat": 41.0620, "lon": 28.9280, "goster": "Eyüpsultan"},
    "fatih":            {"lat": 41.0186, "lon": 28.9397, "goster": "Fatih"},
    "gaziosmanpaşa":    {"lat": 41.0691, "lon": 28.9133, "goster": "Gaziosmanpaşa"},
    "güngören":         {"lat": 41.0191, "lon": 28.8743, "goster": "Güngören"},
    "kadıköy":          {"lat": 40.9819, "lon": 29.0811, "goster": "Kadıköy"},
    "kağıthane":        {"lat": 41.0811, "lon": 28.9706, "goster": "Kağıthane"},
    "kartal":           {"lat": 40.8894, "lon": 29.1867, "goster": "Kartal"},
    "küçükçekmece":     {"lat": 41.0019, "lon": 28.7769, "goster": "Küçükçekmece"},
    "maltepe":          {"lat": 40.9351, "lon": 29.1319, "goster": "Maltepe"},
    "pendik":           {"lat": 40.8738, "lon": 29.2580, "goster": "Pendik"},
    "sancaktepe":       {"lat": 41.0003, "lon": 29.2231, "goster": "Sancaktepe"},
    "sarıyer":          {"lat": 41.1673, "lon": 29.0565, "goster": "Sarıyer"},
    "silivri":          {"lat": 41.0732, "lon": 28.2487, "goster": "Silivri"},
    "sultangazi":       {"lat": 41.1073, "lon": 28.8719, "goster": "Sultangazi"},
    "şile":             {"lat": 41.1761, "lon": 29.6108, "goster": "Şile"},
    "şişli":            {"lat": 41.0602, "lon": 28.9877, "goster": "Şişli"},
    "tuzla":            {"lat": 40.8166, "lon": 29.3009, "goster": "Tuzla"},
    "ümraniye":         {"lat": 41.0165, "lon": 29.1249, "goster": "Ümraniye"},
    "üsküdar":          {"lat": 41.0231, "lon": 29.0151, "goster": "Üsküdar"},
    "zeytinburnu":      {"lat": 41.0001, "lon": 28.9009, "goster": "Zeytinburnu"},

    # ── ANKARA (merkez + ilçeler) ──────────────────────────────
    "ankara":           {"lat": 39.9334, "lon": 32.8597, "goster": "Ankara"},
    "altındağ":         {"lat": 39.9500, "lon": 32.8833, "goster": "Altındağ"},
    "çankaya":          {"lat": 39.9032, "lon": 32.8597, "goster": "Çankaya"},
    "etimesgut":        {"lat": 39.9486, "lon": 32.6741, "goster": "Etimesgut"},
    "gölbaşı":          {"lat": 39.7888, "lon": 32.8056, "goster": "Gölbaşı (Ankara)"},
    "keçiören":         {"lat": 39.9833, "lon": 32.8667, "goster": "Keçiören"},
    "mamak":            {"lat": 39.9286, "lon": 32.9231, "goster": "Mamak"},
    "pursaklar":        {"lat": 40.0333, "lon": 32.9000, "goster": "Pursaklar"},
    "sincan":           {"lat": 39.9738, "lon": 32.5832, "goster": "Sincan"},
    "yenimahalle":      {"lat": 39.9667, "lon": 32.8000, "goster": "Yenimahalle"},

    # ── İZMİR (merkez + ilçeler) ──────────────────────────────
    "izmir":            {"lat": 38.4192, "lon": 27.1287, "goster": "İzmir"},
    "aliağa":           {"lat": 38.8003, "lon": 26.9742, "goster": "Aliağa"},
    "balçova":          {"lat": 38.3888, "lon": 27.0578, "goster": "Balçova"},
    "bayındır":         {"lat": 38.2183, "lon": 27.6470, "goster": "Bayındır"},
    "bergama":          {"lat": 39.1219, "lon": 27.1783, "goster": "Bergama"},
    "bornova":          {"lat": 38.4606, "lon": 27.2171, "goster": "Bornova"},
    "buca":             {"lat": 38.3830, "lon": 27.1809, "goster": "Buca"},
    "çiğli":            {"lat": 38.5159, "lon": 27.0633, "goster": "Çiğli"},
    "gaziemir":         {"lat": 38.3219, "lon": 27.1387, "goster": "Gaziemir"},
    "güzelbahçe":       {"lat": 38.3670, "lon": 26.9013, "goster": "Güzelbahçe"},
    "karabağlar":       {"lat": 38.3712, "lon": 27.1363, "goster": "Karabağlar"},
    "karşıyaka":        {"lat": 38.4581, "lon": 27.1103, "goster": "Karşıyaka"},
    "kemalpaşa":        {"lat": 38.4277, "lon": 27.4238, "goster": "Kemalpaşa"},
    "konak":            {"lat": 38.4122, "lon": 27.1383, "goster": "Konak"},
    "menderes":         {"lat": 38.2545, "lon": 27.1303, "goster": "Menderes"},
    "menemen":          {"lat": 38.6072, "lon": 27.0611, "goster": "Menemen"},
    "narlıdere":        {"lat": 38.3988, "lon": 26.9897, "goster": "Narlıdere"},
    "ödemiş":           {"lat": 38.2278, "lon": 27.9716, "goster": "Ödemiş"},
    "selçuk":           {"lat": 37.9511, "lon": 27.3672, "goster": "Selçuk"},
    "tire":             {"lat": 38.0928, "lon": 27.7364, "goster": "Tire"},
    "torbalı":          {"lat": 38.1611, "lon": 27.3611, "goster": "Torbalı"},
    "urla":             {"lat": 38.3231, "lon": 26.7633, "goster": "Urla"},

    # ── BURSA (merkez + ilçeler) ───────────────────────────────
    "bursa":            {"lat": 40.1885, "lon": 29.0610, "goster": "Bursa"},
    "gemlik":           {"lat": 40.4333, "lon": 29.1667, "goster": "Gemlik"},
    "gürsu":            {"lat": 40.2183, "lon": 29.1672, "goster": "Gürsu"},
    "inegöl":           {"lat": 40.0833, "lon": 29.5167, "goster": "İnegöl"},
    "mudanya":          {"lat": 40.3741, "lon": 28.8853, "goster": "Mudanya"},
    "mustafakemalpaşa": {"lat": 40.0333, "lon": 28.4000, "goster": "Mustafakemalpaşa"},
    "nilüfer":          {"lat": 40.2167, "lon": 28.9667, "goster": "Nilüfer"},
    "osmangazi":        {"lat": 40.1983, "lon": 29.0607, "goster": "Osmangazi"},
    "yıldırım":         {"lat": 40.1833, "lon": 29.1000, "goster": "Yıldırım"},

    # ── ANTALYA (merkez + ilçeler) ─────────────────────────────
    "antalya":          {"lat": 36.8969, "lon": 30.7133, "goster": "Antalya"},
    "alanya":           {"lat": 36.5436, "lon": 32.0022, "goster": "Alanya"},
    "kaş":              {"lat": 36.2003, "lon": 29.6394, "goster": "Kaş"},
    "kemer":            {"lat": 36.5992, "lon": 30.5581, "goster": "Kemer"},
    "kepez":            {"lat": 37.0167, "lon": 30.7333, "goster": "Kepez"},
    "konyaaltı":        {"lat": 36.8667, "lon": 30.6167, "goster": "Konyaaltı"},
    "kumluca":          {"lat": 36.3703, "lon": 30.2867, "goster": "Kumluca"},
    "lara":             {"lat": 36.8500, "lon": 30.7833, "goster": "Lara"},
    "manavgat":         {"lat": 36.7833, "lon": 31.4333, "goster": "Manavgat"},
    "muratpaşa":        {"lat": 36.8833, "lon": 30.7000, "goster": "Muratpaşa"},
    "serik":            {"lat": 36.9167, "lon": 31.1000, "goster": "Serik"},
    "side":             {"lat": 36.7717, "lon": 31.3897, "goster": "Side"},

    # ── ADANA ─────────────────────────────────────────────────
    "adana":            {"lat": 37.0000, "lon": 35.3213, "goster": "Adana"},
    "ceyhan":           {"lat": 37.0250, "lon": 35.8130, "goster": "Ceyhan"},
    "çukurova":         {"lat": 37.0500, "lon": 35.3667, "goster": "Çukurova"},
    "kozan":            {"lat": 37.4500, "lon": 35.8167, "goster": "Kozan"},
    "seyhan":           {"lat": 37.0000, "lon": 35.3333, "goster": "Seyhan"},
    "yüreğir":          {"lat": 36.9833, "lon": 35.3833, "goster": "Yüreğir"},

    # ── KOCAELİ (İZMİT) ───────────────────────────────────────
    "kocaeli":          {"lat": 40.7654, "lon": 29.9408, "goster": "Kocaeli"},
    "izmit":            {"lat": 40.7654, "lon": 29.9408, "goster": "İzmit"},
    "darıca":           {"lat": 40.7667, "lon": 29.8000, "goster": "Darıca"},
    "gebze":            {"lat": 40.8028, "lon": 29.4306, "goster": "Gebze"},
    "gölcük":           {"lat": 40.7167, "lon": 29.8333, "goster": "Gölcük"},
    "körfez":           {"lat": 40.7667, "lon": 29.9167, "goster": "Körfez"},

    # ── MERSİN ────────────────────────────────────────────────
    "mersin":           {"lat": 36.8000, "lon": 34.6333, "goster": "Mersin"},
    "akdeniz":          {"lat": 36.8000, "lon": 34.6333, "goster": "Akdeniz (Mersin)"},
    "erdemli":          {"lat": 36.6108, "lon": 34.3144, "goster": "Erdemli"},
    "silifke":          {"lat": 36.3781, "lon": 33.9308, "goster": "Silifke"},
    "tarsus":           {"lat": 36.9167, "lon": 34.9000, "goster": "Tarsus"},
    "toroslar":         {"lat": 36.7933, "lon": 34.6161, "goster": "Toroslar"},
    "yenişehir":        {"lat": 36.7897, "lon": 34.6203, "goster": "Yenişehir (Mersin)"},

    # ── GAZİANTEP ─────────────────────────────────────────────
    "gaziantep":        {"lat": 37.0662, "lon": 37.3833, "goster": "Gaziantep"},
    "nizip":            {"lat": 37.0094, "lon": 37.7961, "goster": "Nizip"},
    "nurdağı":          {"lat": 37.1800, "lon": 36.7300, "goster": "Nurdağı"},
    "şahinbey":         {"lat": 37.0662, "lon": 37.3556, "goster": "Şahinbey"},
    "şehitkamil":       {"lat": 37.0833, "lon": 37.3833, "goster": "Şehitkamil"},

    # ── KONYA ─────────────────────────────────────────────────
    "konya":            {"lat": 37.8667, "lon": 32.4833, "goster": "Konya"},
    "ereğli":           {"lat": 37.5167, "lon": 34.0500, "goster": "Ereğli (Konya)"},
    "karatay":          {"lat": 37.8833, "lon": 32.5333, "goster": "Karatay"},
    "meram":            {"lat": 37.8500, "lon": 32.4500, "goster": "Meram"},
    "selçuklu":         {"lat": 37.9167, "lon": 32.5000, "goster": "Selçuklu"},

    # ── DİYARBAKIR ────────────────────────────────────────────
    "diyarbakır":       {"lat": 37.9144, "lon": 40.2306, "goster": "Diyarbakır"},
    "bağlar":           {"lat": 37.9167, "lon": 40.2000, "goster": "Bağlar"},
    "kayapınar":        {"lat": 37.9167, "lon": 40.2833, "goster": "Kayapınar"},
    "sur":              {"lat": 37.9167, "lon": 40.2333, "goster": "Sur"},
    "yenişehir":        {"lat": 37.9167, "lon": 40.2500, "goster": "Yenişehir (Diyarbakır)"},

    # ── ŞANLIURFA ─────────────────────────────────────────────
    "şanlıurfa":        {"lat": 37.1591, "lon": 38.7969, "goster": "Şanlıurfa"},
    "birecik":          {"lat": 37.0333, "lon": 37.9833, "goster": "Birecik"},
    "eyyübiye":         {"lat": 37.1667, "lon": 38.8167, "goster": "Eyyübiye"},
    "haliliye":         {"lat": 37.1500, "lon": 38.7667, "goster": "Haliliye"},
    "karaköprü":        {"lat": 37.1833, "lon": 38.7500, "goster": "Karaköprü"},
    "viranşehir":       {"lat": 37.2333, "lon": 39.7667, "goster": "Viranşehir"},

    # ── HATAY ─────────────────────────────────────────────────
    "hatay":            {"lat": 36.4018, "lon": 36.3498, "goster": "Hatay"},
    "antakya":          {"lat": 36.2063, "lon": 36.1603, "goster": "Antakya"},
    "iskenderun":       {"lat": 36.5853, "lon": 36.1656, "goster": "İskenderun"},
    "dörtyol":          {"lat": 36.8481, "lon": 36.2239, "goster": "Dörtyol"},
    "reyhanlı":         {"lat": 36.2667, "lon": 36.5667, "goster": "Reyhanlı"},
    "samandağ":         {"lat": 36.0678, "lon": 35.9844, "goster": "Samandağ"},

    # ── MANİSA ────────────────────────────────────────────────
    "manisa":           {"lat": 38.6191, "lon": 27.4289, "goster": "Manisa"},
    "akhisar":          {"lat": 38.9167, "lon": 27.8333, "goster": "Akhisar"},
    "alaşehir":         {"lat": 38.3500, "lon": 28.5167, "goster": "Alaşehir"},
    "salihli":          {"lat": 38.4833, "lon": 28.1500, "goster": "Salihli"},
    "soma":             {"lat": 39.1833, "lon": 27.6000, "goster": "Soma"},
    "turgutlu":         {"lat": 38.5000, "lon": 27.7000, "goster": "Turgutlu"},

    # ── SAKARYA (ADAPAZARI) ────────────────────────────────────
    "sakarya":          {"lat": 40.7731, "lon": 30.3948, "goster": "Sakarya"},
    "adapazarı":        {"lat": 40.7731, "lon": 30.3948, "goster": "Adapazarı"},
    "arifiye":          {"lat": 40.7500, "lon": 30.3667, "goster": "Arifiye"},
    "erenler":          {"lat": 40.7500, "lon": 30.4167, "goster": "Erenler"},
    "serdivan":         {"lat": 40.7833, "lon": 30.4333, "goster": "Serdivan"},

    # ── TRABZON ───────────────────────────────────────────────
    "trabzon":          {"lat": 41.0015, "lon": 39.7178, "goster": "Trabzon"},
    "akçaabat":         {"lat": 40.9972, "lon": 39.5681, "goster": "Akçaabat"},
    "araklı":           {"lat": 40.9500, "lon": 40.0333, "goster": "Araklı"},
    "of":               {"lat": 40.9500, "lon": 40.2667, "goster": "Of"},
    "ortahisar":        {"lat": 41.0000, "lon": 39.7167, "goster": "Ortahisar (Trabzon)"},

    # ── SAMSUN ────────────────────────────────────────────────
    "samsun":           {"lat": 41.2867, "lon": 36.3300, "goster": "Samsun"},
    "atakum":           {"lat": 41.3333, "lon": 36.2333, "goster": "Atakum"},
    "bafra":            {"lat": 41.5667, "lon": 35.9000, "goster": "Bafra"},
    "canik":            {"lat": 41.2833, "lon": 36.3500, "goster": "Canik"},
    "çarşamba":         {"lat": 41.2000, "lon": 36.7333, "goster": "Çarşamba"},
    "ilkadım":          {"lat": 41.2833, "lon": 36.3333, "goster": "İlkadım"},
    "tekkeköy":         {"lat": 41.2000, "lon": 36.4667, "goster": "Tekkeköy"},

    # ── ESKİŞEHİR ─────────────────────────────────────────────
    "eskişehir":        {"lat": 39.7767, "lon": 30.5206, "goster": "Eskişehir"},
    "odunpazarı":       {"lat": 39.7667, "lon": 30.5333, "goster": "Odunpazarı"},
    "tepebaşı":         {"lat": 39.7833, "lon": 30.5000, "goster": "Tepebaşı"},

    # ── DENİZLİ ───────────────────────────────────────────────
    "denizli":          {"lat": 37.7765, "lon": 29.0864, "goster": "Denizli"},
    "merkezefendi":     {"lat": 37.7833, "lon": 29.0833, "goster": "Merkezefendi"},
    "pamukkale":        {"lat": 37.9167, "lon": 29.1167, "goster": "Pamukkale"},

    # ── MALATYA ───────────────────────────────────────────────
    "malatya":          {"lat": 38.3552, "lon": 38.3095, "goster": "Malatya"},
    "battalgazi":       {"lat": 38.3833, "lon": 38.3500, "goster": "Battalgazi"},
    "yeşilyurt":        {"lat": 38.3500, "lon": 38.2833, "goster": "Yeşilyurt"},

    # ── KAYSERİ ───────────────────────────────────────────────
    "kayseri":          {"lat": 38.7312, "lon": 35.4787, "goster": "Kayseri"},
    "develi":           {"lat": 38.3833, "lon": 35.4833, "goster": "Develi"},
    "kocasinan":        {"lat": 38.7667, "lon": 35.5167, "goster": "Kocasinan"},
    "melikgazi":        {"lat": 38.7167, "lon": 35.4667, "goster": "Melikgazi"},
    "talas":            {"lat": 38.6833, "lon": 35.5500, "goster": "Talas"},

    # ── BALIKESİR ─────────────────────────────────────────────
    "balıkesir":        {"lat": 39.6484, "lon": 27.8826, "goster": "Balıkesir"},
    "ayvalık":          {"lat": 39.3125, "lon": 26.6978, "goster": "Ayvalık"},
    "bandırma":         {"lat": 40.3500, "lon": 27.9667, "goster": "Bandırma"},
    "edremit":          {"lat": 39.5942, "lon": 27.0236, "goster": "Edremit"},
    "gönen":            {"lat": 40.1000, "lon": 27.6500, "goster": "Gönen"},

    # ── ÇORUM ─────────────────────────────────────────────────
    "çorum":            {"lat": 40.5489, "lon": 34.9533, "goster": "Çorum"},

    # ── AFYONKARAHISAR ────────────────────────────────────────
    "afyonkarahisar":   {"lat": 38.7507, "lon": 30.5567, "goster": "Afyonkarahisar"},
    "afyon":            {"lat": 38.7507, "lon": 30.5567, "goster": "Afyon"},

    # ── TEKİRDAĞ ──────────────────────────────────────────────
    "tekirdağ":         {"lat": 40.9833, "lon": 27.5167, "goster": "Tekirdağ"},
    "çerkezköy":        {"lat": 41.2833, "lon": 27.9833, "goster": "Çerkezköy"},
    "çorlu":            {"lat": 41.1575, "lon": 27.8014, "goster": "Çorlu"},
    "süleymanpaşa":     {"lat": 40.9500, "lon": 27.5500, "goster": "Süleymanpaşa"},

    # ── ŞIRNAK ────────────────────────────────────────────────
    "şırnak":           {"lat": 37.5186, "lon": 42.4611, "goster": "Şırnak"},
    "cizre":            {"lat": 37.3286, "lon": 42.1839, "goster": "Cizre"},
    "silopi":           {"lat": 37.2500, "lon": 42.4667, "goster": "Silopi"},

    # ── MARDİN ────────────────────────────────────────────────
    "mardin":           {"lat": 37.3212, "lon": 40.7245, "goster": "Mardin"},
    "kızıltepe":        {"lat": 37.1917, "lon": 40.5858, "goster": "Kızıltepe"},
    "nusaybin":         {"lat": 37.0667, "lon": 41.2167, "goster": "Nusaybin"},

    # ── VAN ───────────────────────────────────────────────────
    "van":              {"lat": 38.4891, "lon": 43.4089, "goster": "Van"},
    "erciş":            {"lat": 39.0167, "lon": 43.3500, "goster": "Erciş"},
    "tuşba":            {"lat": 38.5000, "lon": 43.4167, "goster": "Tuşba"},

    # ── DIĞER İLLER (81 ilin tamamı) ──────────────────────────
    "adıyaman":         {"lat": 37.7648, "lon": 38.2786, "goster": "Adıyaman"},
    "ağrı":             {"lat": 39.7191, "lon": 43.0503, "goster": "Ağrı"},
    "aksaray":          {"lat": 38.3687, "lon": 34.0370, "goster": "Aksaray"},
    "amasya":           {"lat": 40.6499, "lon": 35.8353, "goster": "Amasya"},
    "ardahan":          {"lat": 41.1105, "lon": 42.7022, "goster": "Ardahan"},
    "artvin":           {"lat": 41.1828, "lon": 41.8183, "goster": "Artvin"},
    "aydın":            {"lat": 37.8444, "lon": 27.8458, "goster": "Aydın"},
    "bartın":           {"lat": 41.6344, "lon": 32.3375, "goster": "Bartın"},
    "batman":           {"lat": 37.8812, "lon": 41.1351, "goster": "Batman"},
    "bayburt":          {"lat": 40.2552, "lon": 40.2249, "goster": "Bayburt"},
    "bilecik":          {"lat": 40.1500, "lon": 29.9833, "goster": "Bilecik"},
    "bingöl":           {"lat": 38.8854, "lon": 40.4983, "goster": "Bingöl"},
    "bitlis":           {"lat": 38.4003, "lon": 42.1217, "goster": "Bitlis"},
    "bolu":             {"lat": 40.7353, "lon": 31.6061, "goster": "Bolu"},
    "burdur":           {"lat": 37.7167, "lon": 30.2833, "goster": "Burdur"},
    "çanakkale":        {"lat": 40.1553, "lon": 26.4142, "goster": "Çanakkale"},
    "düzce":            {"lat": 40.8438, "lon": 31.1565, "goster": "Düzce"},
    "edirne":           {"lat": 41.6818, "lon": 26.5623, "goster": "Edirne"},
    "elazığ":           {"lat": 38.6810, "lon": 39.2264, "goster": "Elazığ"},
    "erzincan":         {"lat": 39.7500, "lon": 39.5000, "goster": "Erzincan"},
    "erzurum":          {"lat": 39.9055, "lon": 41.2658, "goster": "Erzurum"},
    "giresun":          {"lat": 40.9128, "lon": 38.3895, "goster": "Giresun"},
    "gümüşhane":        {"lat": 40.4386, "lon": 39.4814, "goster": "Gümüşhane"},
    "hakkari":          {"lat": 37.5744, "lon": 43.7408, "goster": "Hakkari"},
    "ığdır":            {"lat": 39.9167, "lon": 44.0333, "goster": "Iğdır"},
    "ısparta":          {"lat": 37.7648, "lon": 30.5566, "goster": "Isparta"},
    "karabük":          {"lat": 41.2061, "lon": 32.6204, "goster": "Karabük"},
    "karaman":          {"lat": 37.1759, "lon": 33.2287, "goster": "Karaman"},
    "kars":             {"lat": 40.6167, "lon": 43.1000, "goster": "Kars"},
    "kastamonu":        {"lat": 41.3887, "lon": 33.7827, "goster": "Kastamonu"},
    "kırıkkale":        {"lat": 39.8468, "lon": 33.5153, "goster": "Kırıkkale"},
    "kırklareli":       {"lat": 41.7333, "lon": 27.2167, "goster": "Kırklareli"},
    "kırşehir":         {"lat": 39.1425, "lon": 34.1709, "goster": "Kırşehir"},
    "kilis":            {"lat": 36.7184, "lon": 37.1212, "goster": "Kilis"},
    "kütahya":          {"lat": 39.4167, "lon": 29.9833, "goster": "Kütahya"},
    "muğla":            {"lat": 37.2153, "lon": 28.3636, "goster": "Muğla"},
    "muş":              {"lat": 38.9462, "lon": 41.7539, "goster": "Muş"},
    "nevşehir":         {"lat": 38.6939, "lon": 34.6857, "goster": "Nevşehir"},
    "niğde":            {"lat": 37.9667, "lon": 34.6833, "goster": "Niğde"},
    "ordu":             {"lat": 40.9839, "lon": 37.8764, "goster": "Ordu"},
    "osmaniye":         {"lat": 37.0742, "lon": 36.2478, "goster": "Osmaniye"},
    "rize":             {"lat": 41.0201, "lon": 40.5234, "goster": "Rize"},
    "siirt":            {"lat": 37.9333, "lon": 41.9500, "goster": "Siirt"},
    "sinop":            {"lat": 42.0231, "lon": 35.1531, "goster": "Sinop"},
    "sivas":            {"lat": 39.7477, "lon": 37.0179, "goster": "Sivas"},
    "tokat":            {"lat": 40.3167, "lon": 36.5500, "goster": "Tokat"},
    "tunçeli":          {"lat": 39.1079, "lon": 39.5401, "goster": "Tunceli"},
    "uşak":             {"lat": 38.6823, "lon": 29.4082, "goster": "Uşak"},
    "yalova":           {"lat": 40.6500, "lon": 29.2667, "goster": "Yalova"},
    "yozgat":           {"lat": 39.8181, "lon": 34.8147, "goster": "Yozgat"},
    "zonguldak":        {"lat": 41.4564, "lon": 31.7987, "goster": "Zonguldak"},

    # ── TURİSTİK / POPÜLER YERLER ─────────────────────────────
    "bodrum":           {"lat": 37.0344, "lon": 27.4305, "goster": "Bodrum"},
    "fethiye":          {"lat": 36.6558, "lon": 29.1228, "goster": "Fethiye"},
    "marmaris":         {"lat": 36.8561, "lon": 28.2711, "goster": "Marmaris"},
    "didim":            {"lat": 37.3706, "lon": 27.2681, "goster": "Didim"},
    "kuşadası":         {"lat": 37.8564, "lon": 27.2589, "goster": "Kuşadası"},
    "çeşme":            {"lat": 38.3236, "lon": 26.3036, "goster": "Çeşme"},
    "kapadokya":        {"lat": 38.6431, "lon": 34.8289, "goster": "Kapadokya"},
    "göreme":           {"lat": 38.6431, "lon": 34.8289, "goster": "Göreme"},
    "pamukkale":        {"lat": 37.9208, "lon": 29.1208, "goster": "Pamukkale"},
    "efes":             {"lat": 37.9397, "lon": 27.3414, "goster": "Efes"},
    "bozcaada":         {"lat": 39.8333, "lon": 26.0667, "goster": "Bozcaada"},
    "gökçeada":         {"lat": 40.1667, "lon": 25.9000, "goster": "Gökçeada"},
    "sapanca":          {"lat": 40.6920, "lon": 30.2672, "goster": "Sapanca"},
    "abant":            {"lat": 40.6783, "lon": 31.2797, "goster": "Abant"},
    "uludağ":           {"lat": 40.1167, "lon": 29.0667, "goster": "Uludağ"},
    "kaçkar":           {"lat": 40.8167, "lon": 41.1500, "goster": "Kaçkar"},
    "nemrut":           {"lat": 37.9811, "lon": 38.7417, "goster": "Nemrut Dağı"},
}

HAVA_TR = {
    # Thunderstorm
    "thunderstorm with light rain": "hafif yağmurlu fırtınalı",
    "thunderstorm with rain": "yağmurlu fırtınalı",
    "thunderstorm with heavy rain": "şiddetli yağmurlu fırtınalı",
    "light thunderstorm": "hafif fırtınalı",
    "thunderstorm": "fırtınalı",
    "heavy thunderstorm": "şiddetli fırtınalı",
    "ragged thunderstorm": "düzensiz fırtınalı",
    "thunderstorm with light drizzle": "hafif çiseleyen fırtınalı",
    "thunderstorm with drizzle": "çiseleyen fırtınalı",
    "thunderstorm with heavy drizzle": "yoğun çiseleyen fırtınalı",
    # Drizzle
    "light intensity drizzle": "hafif çiseleyen",
    "drizzle": "çiseleyen",
    "heavy intensity drizzle": "yoğun çiseleyen",
    "light intensity drizzle rain": "hafif çiseleme yağışlı",
    "drizzle rain": "çiseleme yağışlı",
    "heavy intensity drizzle rain": "yoğun çiseleme yağışlı",
    "shower rain and drizzle": "sağanak ve çiseleme",
    "heavy shower rain and drizzle": "yoğun sağanak ve çiseleme",
    "shower drizzle": "sağanak çiseleyen",
    # Rain
    "light rain": "hafif yağmurlu",
    "moderate rain": "orta şiddetli yağmurlu",
    "heavy intensity rain": "yoğun yağmurlu",
    "very heavy rain": "çok yoğun yağmurlu",
    "extreme rain": "aşırı yağmurlu",
    "freezing rain": "dondurucu yağmurlu",
    "light intensity shower rain": "hafif sağanaklı",
    "shower rain": "sağanaklı",
    "heavy intensity shower rain": "yoğun sağanaklı",
    "ragged shower rain": "düzensiz sağanaklı",
    # Snow
    "light snow": "hafif karlı",
    "snow": "karlı",
    "heavy snow": "yoğun karlı",
    "sleet": "karla karışık yağmurlu",
    "light shower sleet": "hafif karla karışık sağanaklı",
    "shower sleet": "karla karışık sağanaklı",
    "light rain and snow": "hafif yağmur ve kar",
    "rain and snow": "yağmur ve kar",
    "light shower snow": "hafif kar sağanaklı",
    "shower snow": "kar sağanaklı",
    "heavy shower snow": "yoğun kar sağanaklı",
    # Atmosphere
    "mist": "sisli",
    "smoke": "dumanlı",
    "haze": "puslu",
    "sand/dust whirls": "kum/toz girdabı",
    "fog": "yoğun sisli",
    "sand": "kumlu",
    "dust": "tozlu",
    "volcanic ash": "volkanik küllü",
    "squalls": "ani fırtınalı",
    "tornado": "kasırgalı",
    # Clear & Clouds
    "clear sky": "açık",
    "few clouds": "az bulutlu",
    "scattered clouds": "parçalı bulutlu",
    "broken clouds": "çok bulutlu",
    "overcast clouds": "kapalı",
}

# Renkler
COLORS = {
    "kirmizi": (255, 0, 0),
    "turuncu": (255, 128, 0),
    "sari": (255, 255, 0),
    "yesil": (0, 255, 0),
    "turkuaz": (0, 255, 234),
    "mavi": (0, 0, 255),
    "lacivert": (0, 0, 128),
    "mor": (128, 0, 255),
    "pembe": (255, 0, 128),
    "magenta": (255, 0, 255),
    "beyaz": (255, 255, 255),
    "sicak beyaz": (255, 217, 178),
    "gun isigi": (204, 230, 255),
    "lavanta": (172, 115, 230),
    "mercan": (255, 87, 25),
    "limon": (238, 255, 51),
    "gokyuzu": (102, 204, 255),
    "amber": (204, 136, 0),
    "mint": (92, 230, 161),
    "fusya": (255, 0, 191),
    "eflatun": (203, 69, 230),
    "seftali": (255, 170, 128),
    "buz mavisi": (145, 218, 242),
    "gun batimi": (230, 122, 46),
    "okyanus": (25, 140, 255),
}

COLORS_TR = {
    "kirmizi": "kırmızı",
    "turuncu": "turuncu",
    "sari": "sarı",
    "yesil": "yeşil",
    "turkuaz": "turkuaz",
    "mavi": "mavi",
    "lacivert": "lacivert",
    "mor": "mor",
    "pembe": "pembe",
    "magenta": "magenta",
    "beyaz": "beyaz",
    "sicak beyaz": "sıcak beyaz",
    "gun isigi": "gün ışığı",
    "lavanta": "lavanta",
    "mercan": "mercan",
    "limon": "limon",
    "gokyuzu": "gökyüzü",
    "amber": "amber",
    "mint": "mint",
    "fusya": "fuşya",
    "eflatun": "eflatun",
    "seftali": "şeftali",
    "buz mavisi": "buz mavisi",
    "gun batimi": "gün batımı",
    "okyanus": "okyanus",
}

# Uygulama İsimleri Eşleştirmesi
UYGULAMALAR = {
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "firefox": "Firefox",
    "mozilla": "Firefox",
    "edge": "Microsoft Edge",
    "microsoft edge": "Microsoft Edge",
    "opera": "Opera",
    "brave": "Brave",
    "word": "Microsoft Word",
    "excel": "Microsoft Excel",
    "powerpoint": "Microsoft PowerPoint",
    "outlook": "Microsoft Outlook",
    "onenote": "OneNote",
    "notepad": "Notepad",
    "not defteri": "Notepad",
    "wordpad": "WordPad",
    "libreoffice": "LibreOffice",
    "notion": "Notion",
    "obsidian": "Obsidian",
    "evernote": "Evernote",
    "vscode": "Visual Studio Code",
    "visual studio code": "Visual Studio Code",
    "vs code": "Visual Studio Code",
    "visual studio": "Visual Studio",
    "pycharm": "PyCharm",
    "android studio": "Android Studio",
    "terminal": "Command Prompt",
    "cmd": "Command Prompt",
    "komut istemi": "Command Prompt",
    "powershell": "PowerShell",
    "git bash": "Git Bash",
    "wsl": "WSL",
    "postman": "Postman",
    "dbeaver": "DBeaver",
    "docker": "Docker Desktop",
    "spotify": "Spotify",
    "vlc": "VLC",
    "netflix": "Netflix",
    "youtube": "YouTube",
    "prime": "Prime Video",
    "amazon prime": "Prime Video",
    "disney": "Disney Plus",
    "disneyplus": "Disney Plus",
    "twitch": "Twitch",
    "plex": "Plex",
    "media player": "Windows Media Player",
    "groove": "Groove Music",
    "itunes": "iTunes",
    "mubi": "MUBI",
    "blutv": "BluTV",
    "gain": "Gain",
    "exxen": "Exxen",
    "steam": "Steam",
    "epic": "Epic Games",
    "epic games": "Epic Games",
    "xbox": "Xbox",
    "gog": "GOG Galaxy",
    "battle net": "Battle.net",
    "battlenet": "Battle.net",
    "ubisoft": "Ubisoft Connect",
    "origin": "EA App",
    "ea": "EA App",
    "minecraft": "Minecraft",
    "roblox": "Roblox",
    "discord": "Discord",
    "whatsapp": "WhatsApp",
    "telegram": "Telegram",
    "zoom": "Zoom",
    "teams": "Microsoft Teams",
    "skype": "Skype",
    "slack": "Slack",
    "signal": "Signal",
    "viber": "Viber",
    "webex": "Webex",
    "gorev yoneticisi": "Task Manager",
    "hesap makinesi": "Calculator",
    "boya": "Paint",
    "paint": "Paint",
    "dosya gezgini": "File Explorer",
    "ayarlar": "Settings",
    "denetim masasi": "Control Panel",
    "snipping tool": "Snipping Tool",
    "ekran alintisi": "Snipping Tool",
    "kayit defteri": "Registry Editor",
    "disk yoneticisi": "Disk Management",
    "photoshop": "Adobe Photoshop",
    "illustrator": "Adobe Illustrator",
    "premiere": "Adobe Premiere Pro",
    "after effects": "Adobe After Effects",
    "lightroom": "Adobe Lightroom",
    "figma": "Figma",
    "gimp": "GIMP",
    "inkscape": "Inkscape",
    "davinci": "DaVinci Resolve",
    "davinci resolve": "DaVinci Resolve",
    "blender": "Blender",
    "canva": "Canva",
    "capcut": "CapCut",
    "nordvpn": "NordVPN",
    "expressvpn": "ExpressVPN",
    "malwarebytes": "Malwarebytes",
    "avast": "Avast",
    "kaspersky": "Kaspersky",
    "onedrive": "OneDrive",
    "dropbox": "Dropbox",
    "google drive": "Google Drive",
    "mega": "MEGA",
    "7zip": "7-Zip",
    "winrar": "WinRAR",
    "ccleaner": "CCleaner",
    "anki": "Anki",
    "audacity": "Audacity",
    "obs": "OBS Studio",
    "obs studio": "OBS Studio",
    "anydesk": "AnyDesk",
    "teamviewer": "TeamViewer",
    "rufus": "Rufus",
    "bitwarden": "Bitwarden",
    "keepass": "KeePass",
}

# Türkçe ekler (normalizasyon için)
_TR_EKLER = sorted([
    "netflixi", "netflixe", "netflixten",
    "'yi", "\u2019yi", "'yu", "\u2019yu",
    "den", "dan", "ten", "tan",
    "nin", "nun", "nun", "nun",
    "ye", "ya", "te", "ta", "de", "da",
    "yi", "yu", "yi", "yu",
    "ni", "nu", "ni", "nu",
    "i", "u", "i", "u",
    "e", "a",
], key=len, reverse=True)

BEYAZ_TONLAR = {"beyaz": 1000, "sicak beyaz": 100, "gun isigi": 600}

VERA_SISTEM_MESAJI = (
    "Senin adın Vera. Türkçe konuşan, sıcak, esprili ve yardımsever bir "
    "sesli ev asistanısın. Tıpkı normal bir yapay zeka sohbet botu gibi "
    "davranabilirsin: genel bilgi sorularını cevaplarsın, sohbet edersin, "
    "fikir paylaşırsın, açıklama yaparsın. "
    "ÖNEMLİ KURALLAR: (1) Cevabın doğrudan sesli olarak okunacak, bu "
    "yüzden HER ZAMAN sadece akıcı, doğal Türkçe konuşma dili kullan; "
    "kısa tut (genelde 1-4 cümle). (2) Madde işareti, numaralı liste, "
    "markdown biçimlendirme, yıldız işareti, emoji KULLANMA - sadece düz "
    "metin. (3) Işık açma/kapama, renk veya parlaklık ayarlama, hava "
    "durumu sorma, uygulama açma, ekran görüntüsü alma, bilgisayarı "
    "kapatma/yeniden başlatma/uyutma/kilitleme gibi komutlar zaten ayrı "
    "bir sistem tarafından otomatik yönetiliyor; bu mesajı görüyorsan "
    "kullanıcı o komutlardan birini söylememiş, yani bu genel bir sohbet "
    "veya bilgi sorusu - ona göre cevap ver."
)

# Güç onay süresi (saniye)
GUC_ONAY_SURE = 15