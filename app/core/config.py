import torch

# --- Audio ---
SAMPLE_RATE = 24000
MP3_BITRATE = "320k"
MP3_BITRATE_STREAM = "256k"

# --- Servidor ---
HOST = "0.0.0.0"
PORT = 8880

# --- Device ---
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# --- Chunking de texto ---
CHUNK_TARGET_MIN_CHARS = 80
CHUNK_TARGET_MAX_CHARS = 250
CHUNK_ABSOLUTE_MAX_CHARS = 450

# --- Crossfade e silêncio ---
CROSSFADE_MS = 50
SILENCE_BETWEEN_CHUNKS_MS = 80

# --- Kokoro / Edge TTS ---
DEFAULT_LANG = "pt-br"
DEFAULT_LANG_CODE = "p"
DEFAULT_VOICE = "pf_dora"

LANGUAGES = {
    "en-us": {
        "id": "en-us",
        "name": "English",
        "label": "Inglês",
        "kokoro_code": "a",
        "supported": True,
        "sample_text": "Hello. This is a multilingual Kokoro voice synthesis test.",
    },
    "de-de": {
        "id": "de-de",
        "name": "Deutsch",
        "label": "Alemão",
        "kokoro_code": None,
        "supported": True,
        "sample_text": "Hallo. Dies ist ein deutscher Sprachsynthese-Test.",
    },
    "fr-fr": {
        "id": "fr-fr",
        "name": "Français",
        "label": "Francês",
        "kokoro_code": "f",
        "supported": True,
        "sample_text": "Bonjour. Ceci est un test de synthèse vocale multilingue avec Kokoro.",
    },
    "ja-jp": {
        "id": "ja-jp",
        "name": "日本語",
        "label": "Japonês",
        "kokoro_code": "j",
        "supported": True,
        "sample_text": "こんにちは。これはKokoroの多言語音声合成テストです。",
    },
    "es-es": {
        "id": "es-es",
        "name": "Español",
        "label": "Espanhol",
        "kokoro_code": "e",
        "supported": True,
        "sample_text": "Hola. Esta es una prueba de síntesis de voz multilingüe con Kokoro.",
    },
    "pt-br": {
        "id": "pt-br",
        "name": "Português",
        "label": "Português",
        "kokoro_code": "p",
        "supported": True,
        "sample_text": "Olá. Este é um teste de síntese de voz multilíngue com Kokoro.",
    },
}

VOICES = {
    "de_f_katja": {
        "id": "de_f_katja",
        "name": "Katja",
        "gender": "feminino",
        "lang": "de-de",
        "lang_code": None,
        "engine": "edge",
        "source": "de-DE-KatjaNeural",
        "description": "Voz feminina em alemão da Alemanha",
    },
    "de_m_conrad": {
        "id": "de_m_conrad",
        "name": "Conrad",
        "gender": "masculino",
        "lang": "de-de",
        "lang_code": None,
        "engine": "edge",
        "source": "de-DE-ConradNeural",
        "description": "Voz masculina em alemão da Alemanha",
    },
    "de_f_leni": {
        "id": "de_f_leni",
        "name": "Leni",
        "gender": "feminino",
        "lang": "de-de",
        "lang_code": None,
        "engine": "edge",
        "source": "de-CH-LeniNeural",
        "description": "Voz feminina em alemão da Suíça",
    },
    "de_m_jonas": {
        "id": "de_m_jonas",
        "name": "Jonas",
        "gender": "masculino",
        "lang": "de-de",
        "lang_code": None,
        "engine": "edge",
        "source": "de-AT-JonasNeural",
        "description": "Voz masculina em alemão da Áustria",
    },
    "af_bella": {
        "id": "af_bella",
        "name": "Bella",
        "gender": "feminino",
        "lang": "en-us",
        "lang_code": "a",
        "engine": "kokoro",
        "source": "models/kokoro_voices/voices/af_bella.pt",
        "description": "Voz feminina em inglês americano",
    },
    "am_adam": {
        "id": "am_adam",
        "name": "Adam",
        "gender": "masculino",
        "lang": "en-us",
        "lang_code": "a",
        "engine": "kokoro",
        "source": "models/kokoro_voices/voices/am_adam.pt",
        "description": "Voz masculina em inglês americano",
    },
    "bf_emma": {
        "id": "bf_emma",
        "name": "Emma",
        "gender": "feminino",
        "lang": "en-us",
        "lang_code": "b",
        "engine": "kokoro",
        "source": "models/kokoro_voices/voices/bf_emma.pt",
        "description": "Voz feminina em inglês britânico",
    },
    "bm_george": {
        "id": "bm_george",
        "name": "George",
        "gender": "masculino",
        "lang": "en-us",
        "lang_code": "b",
        "engine": "kokoro",
        "source": "models/kokoro_voices/voices/bm_george.pt",
        "description": "Voz masculina em inglês britânico",
    },
    "ff_siwis": {
        "id": "ff_siwis",
        "name": "Siwis",
        "gender": "feminino",
        "lang": "fr-fr",
        "lang_code": "f",
        "engine": "kokoro",
        "source": "models/kokoro_voices/voices/ff_siwis.pt",
        "description": "Voz feminina em francês",
    },
    "jf_alpha": {
        "id": "jf_alpha",
        "name": "Alpha",
        "gender": "feminino",
        "lang": "ja-jp",
        "lang_code": "j",
        "engine": "kokoro",
        "source": "models/kokoro_voices/voices/jf_alpha.pt",
        "description": "Voz feminina em japonês",
    },
    "jm_kumo": {
        "id": "jm_kumo",
        "name": "Kumo",
        "gender": "masculino",
        "lang": "ja-jp",
        "lang_code": "j",
        "engine": "kokoro",
        "source": "models/kokoro_voices/voices/jm_kumo.pt",
        "description": "Voz masculina em japonês",
    },
    "ef_dora": {
        "id": "ef_dora",
        "name": "Dora",
        "gender": "feminino",
        "lang": "es-es",
        "lang_code": "e",
        "engine": "kokoro",
        "source": "models/kokoro_voices/voices/ef_dora.pt",
        "description": "Voz feminina em espanhol",
    },
    "em_alex": {
        "id": "em_alex",
        "name": "Alex",
        "gender": "masculino",
        "lang": "es-es",
        "lang_code": "e",
        "engine": "kokoro",
        "source": "models/kokoro_voices/voices/em_alex.pt",
        "description": "Voz masculina em espanhol",
    },
    "em_santa": {
        "id": "em_santa",
        "name": "Santa",
        "gender": "masculino",
        "lang": "es-es",
        "lang_code": "e",
        "engine": "kokoro",
        "source": "models/kokoro_voices/voices/em_santa.pt",
        "description": "Voz masculina em espanhol",
    },
    "pf_dora": {
        "id": "pf_dora",
        "name": "Dora",
        "gender": "feminino",
        "lang": "pt-br",
        "lang_code": "p",
        "engine": "kokoro",
        "description": "Voz feminina brasileira",
    },
    "pm_alex": {
        "id": "pm_alex",
        "name": "Alex",
        "gender": "masculino",
        "lang": "pt-br",
        "lang_code": "p",
        "engine": "kokoro",
        "description": "Voz masculina brasileira",
    },
    "pm_santa": {
        "id": "pm_santa",
        "name": "Santa",
        "gender": "masculino",
        "lang": "pt-br",
        "lang_code": "p",
        "engine": "kokoro",
        "description": "Voz masculina brasileira",
    },
    "pt_f_menina": {
        "id": "pt_f_menina",
        "name": "Menina",
        "gender": "feminino",
        "lang": "pt-br",
        "lang_code": None,
        "engine": "edge",
        "source": "pt-BR-ThalitaMultilingualNeural",
        "default_speed": 1.08,
        "default_pitch": 46,
        "description": "Voz feminina infantil brasileira com timbre mais agudo",
    },
    "pt_m_menino": {
        "id": "pt_m_menino",
        "name": "Menino",
        "gender": "masculino",
        "lang": "pt-br",
        "lang_code": None,
        "engine": "edge",
        "source": "pt-BR-AntonioNeural",
        "default_speed": 1.05,
        "default_pitch": 28,
        "description": "Voz masculina infantil brasileira com timbre mais jovem",
    },
}
