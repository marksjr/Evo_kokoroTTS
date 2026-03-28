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

# --- Crossfade e silencio ---
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
        "label": "Ingles Americano",
        "kokoro_code": "a",
        "supported": True,
        "sample_text": "Hello. This is a multilingual Kokoro voice synthesis test.",
    },
    "en-gb": {
        "id": "en-gb",
        "name": "English",
        "label": "Ingles Britanico",
        "kokoro_code": "b",
        "supported": True,
        "sample_text": "Hello. This is a British English Kokoro voice synthesis test.",
    },
    "de-de": {
        "id": "de-de",
        "name": "Deutsch",
        "label": "Alemao",
        "kokoro_code": None,
        "supported": True,
        "sample_text": "Hallo. Dies ist ein deutscher Sprachsynthese-Test.",
    },
    "fr-fr": {
        "id": "fr-fr",
        "name": "Francais",
        "label": "Frances",
        "kokoro_code": "f",
        "supported": True,
        "sample_text": "Bonjour. Ceci est un test de synthese vocale multilingue avec Kokoro.",
    },
    "ja-jp": {
        "id": "ja-jp",
        "name": "Nihongo",
        "label": "Japones",
        "kokoro_code": "j",
        "supported": True,
        "sample_text": "こんにちは。これはKokoroの多言語音声合成テストです。",
    },
    "zh-cn": {
        "id": "zh-cn",
        "name": "Zhongwen",
        "label": "Chines",
        "kokoro_code": "z",
        "supported": True,
        "sample_text": "你好。这是一个 Kokoro 多语言语音合成测试。",
    },
    "es-es": {
        "id": "es-es",
        "name": "Espanol",
        "label": "Espanhol",
        "kokoro_code": "e",
        "supported": True,
        "sample_text": "Hola. Esta es una prueba de sintesis de voz multilingue con Kokoro.",
    },
    "hi-in": {
        "id": "hi-in",
        "name": "Hindi",
        "label": "Hindi",
        "kokoro_code": "h",
        "supported": True,
        "sample_text": "नमस्ते। यह Kokoro की बहुभाषी वॉइस सिंथेसिस जांच है।",
    },
    "it-it": {
        "id": "it-it",
        "name": "Italiano",
        "label": "Italiano",
        "kokoro_code": "i",
        "supported": True,
        "sample_text": "Ciao. Questo e un test di sintesi vocale multilingue con Kokoro.",
    },
    "pt-br": {
        "id": "pt-br",
        "name": "Portugues",
        "label": "Portugues",
        "kokoro_code": "p",
        "supported": True,
        "sample_text": "Ola. Este e um teste de sintese de voz multilingue com Kokoro.",
    },
}


def kokoro_voice(voice_id: str, name: str, gender: str, lang: str, lang_code: str, description: str) -> dict:
    return {
        "id": voice_id,
        "name": name,
        "gender": gender,
        "lang": lang,
        "lang_code": lang_code,
        "engine": "kokoro",
        "source": f"models/kokoro_voices/voices/{voice_id}.pt",
        "description": description,
    }


def edge_voice(
    voice_id: str,
    name: str,
    gender: str,
    lang: str,
    source: str,
    description: str,
    default_speed: float | None = None,
    default_pitch: int | None = None,
) -> dict:
    voice = {
        "id": voice_id,
        "name": name,
        "gender": gender,
        "lang": lang,
        "lang_code": None,
        "engine": "edge",
        "source": source,
        "description": description,
    }
    if default_speed is not None:
        voice["default_speed"] = default_speed
    if default_pitch is not None:
        voice["default_pitch"] = default_pitch
    return voice


VOICES = {
    "de_f_katja": edge_voice(
        "de_f_katja", "Katja", "feminino", "de-de", "de-DE-KatjaNeural", "Voz feminina em alemao da Alemanha"
    ),
    "de_m_conrad": edge_voice(
        "de_m_conrad", "Conrad", "masculino", "de-de", "de-DE-ConradNeural", "Voz masculina em alemao da Alemanha"
    ),
    "de_f_leni": edge_voice(
        "de_f_leni", "Leni", "feminino", "de-de", "de-CH-LeniNeural", "Voz feminina em alemao da Suica"
    ),
    "de_m_jonas": edge_voice(
        "de_m_jonas", "Jonas", "masculino", "de-de", "de-AT-JonasNeural", "Voz masculina em alemao da Austria"
    ),
    "pt_f_menina": edge_voice(
        "pt_f_menina",
        "Menina",
        "feminino",
        "pt-br",
        "pt-BR-ThalitaMultilingualNeural",
        "Voz feminina infantil brasileira com timbre mais agudo",
        default_speed=1.08,
        default_pitch=46,
    ),
    "pt_m_menino": edge_voice(
        "pt_m_menino",
        "Menino",
        "masculino",
        "pt-br",
        "pt-BR-AntonioNeural",
        "Voz masculina infantil brasileira com timbre mais jovem",
        default_speed=1.05,
        default_pitch=28,
    ),
    "af_heart": kokoro_voice("af_heart", "Heart", "feminino", "en-us", "a", "Voz feminina em ingles americano"),
    "af_alloy": kokoro_voice("af_alloy", "Alloy", "feminino", "en-us", "a", "Voz feminina em ingles americano"),
    "af_aoede": kokoro_voice("af_aoede", "Aoede", "feminino", "en-us", "a", "Voz feminina em ingles americano"),
    "af_bella": kokoro_voice("af_bella", "Bella", "feminino", "en-us", "a", "Voz feminina em ingles americano"),
    "af_jessica": kokoro_voice("af_jessica", "Jessica", "feminino", "en-us", "a", "Voz feminina em ingles americano"),
    "af_kore": kokoro_voice("af_kore", "Kore", "feminino", "en-us", "a", "Voz feminina em ingles americano"),
    "af_nicole": kokoro_voice("af_nicole", "Nicole", "feminino", "en-us", "a", "Voz feminina em ingles americano"),
    "af_nova": kokoro_voice("af_nova", "Nova", "feminino", "en-us", "a", "Voz feminina em ingles americano"),
    "af_river": kokoro_voice("af_river", "River", "feminino", "en-us", "a", "Voz feminina em ingles americano"),
    "af_sarah": kokoro_voice("af_sarah", "Sarah", "feminino", "en-us", "a", "Voz feminina em ingles americano"),
    "af_sky": kokoro_voice("af_sky", "Sky", "feminino", "en-us", "a", "Voz feminina em ingles americano"),
    "am_adam": kokoro_voice("am_adam", "Adam", "masculino", "en-us", "a", "Voz masculina em ingles americano"),
    "am_echo": kokoro_voice("am_echo", "Echo", "masculino", "en-us", "a", "Voz masculina em ingles americano"),
    "am_eric": kokoro_voice("am_eric", "Eric", "masculino", "en-us", "a", "Voz masculina em ingles americano"),
    "am_fenrir": kokoro_voice("am_fenrir", "Fenrir", "masculino", "en-us", "a", "Voz masculina em ingles americano"),
    "am_liam": kokoro_voice("am_liam", "Liam", "masculino", "en-us", "a", "Voz masculina em ingles americano"),
    "am_michael": kokoro_voice("am_michael", "Michael", "masculino", "en-us", "a", "Voz masculina em ingles americano"),
    "am_onyx": kokoro_voice("am_onyx", "Onyx", "masculino", "en-us", "a", "Voz masculina em ingles americano"),
    "am_puck": kokoro_voice("am_puck", "Puck", "masculino", "en-us", "a", "Voz masculina em ingles americano"),
    "am_santa": kokoro_voice("am_santa", "Santa", "masculino", "en-us", "a", "Voz masculina em ingles americano"),
    "bf_alice": kokoro_voice("bf_alice", "Alice", "feminino", "en-gb", "b", "Voz feminina em ingles britanico"),
    "bf_emma": kokoro_voice("bf_emma", "Emma", "feminino", "en-gb", "b", "Voz feminina em ingles britanico"),
    "bf_isabella": kokoro_voice("bf_isabella", "Isabella", "feminino", "en-gb", "b", "Voz feminina em ingles britanico"),
    "bf_lily": kokoro_voice("bf_lily", "Lily", "feminino", "en-gb", "b", "Voz feminina em ingles britanico"),
    "bm_daniel": kokoro_voice("bm_daniel", "Daniel", "masculino", "en-gb", "b", "Voz masculina em ingles britanico"),
    "bm_fable": kokoro_voice("bm_fable", "Fable", "masculino", "en-gb", "b", "Voz masculina em ingles britanico"),
    "bm_george": kokoro_voice("bm_george", "George", "masculino", "en-gb", "b", "Voz masculina em ingles britanico"),
    "bm_lewis": kokoro_voice("bm_lewis", "Lewis", "masculino", "en-gb", "b", "Voz masculina em ingles britanico"),
    "ef_dora": kokoro_voice("ef_dora", "Dora", "feminino", "es-es", "e", "Voz feminina em espanhol"),
    "em_alex": kokoro_voice("em_alex", "Alex", "masculino", "es-es", "e", "Voz masculina em espanhol"),
    "em_santa": kokoro_voice("em_santa", "Santa", "masculino", "es-es", "e", "Voz masculina em espanhol"),
    "ff_siwis": kokoro_voice("ff_siwis", "Siwis", "feminino", "fr-fr", "f", "Voz feminina em frances"),
    "hf_alpha": kokoro_voice("hf_alpha", "Alpha", "feminino", "hi-in", "h", "Voz feminina em hindi"),
    "hf_beta": kokoro_voice("hf_beta", "Beta", "feminino", "hi-in", "h", "Voz feminina em hindi"),
    "hm_omega": kokoro_voice("hm_omega", "Omega", "masculino", "hi-in", "h", "Voz masculina em hindi"),
    "hm_psi": kokoro_voice("hm_psi", "Psi", "masculino", "hi-in", "h", "Voz masculina em hindi"),
    "if_sara": kokoro_voice("if_sara", "Sara", "feminino", "it-it", "i", "Voz feminina em italiano"),
    "im_nicola": kokoro_voice("im_nicola", "Nicola", "masculino", "it-it", "i", "Voz masculina em italiano"),
    "jf_alpha": kokoro_voice("jf_alpha", "Alpha", "feminino", "ja-jp", "j", "Voz feminina em japones"),
    "jf_gongitsune": kokoro_voice("jf_gongitsune", "Gongitsune", "feminino", "ja-jp", "j", "Voz feminina em japones"),
    "jf_nezumi": kokoro_voice("jf_nezumi", "Nezumi", "feminino", "ja-jp", "j", "Voz feminina em japones"),
    "jf_tebukuro": kokoro_voice("jf_tebukuro", "Tebukuro", "feminino", "ja-jp", "j", "Voz feminina em japones"),
    "jm_kumo": kokoro_voice("jm_kumo", "Kumo", "masculino", "ja-jp", "j", "Voz masculina em japones"),
    "pf_dora": kokoro_voice("pf_dora", "Dora", "feminino", "pt-br", "p", "Voz feminina brasileira"),
    "pm_alex": kokoro_voice("pm_alex", "Alex", "masculino", "pt-br", "p", "Voz masculina brasileira"),
    "pm_santa": kokoro_voice("pm_santa", "Santa", "masculino", "pt-br", "p", "Voz masculina brasileira"),
    "zf_xiaobei": kokoro_voice("zf_xiaobei", "Xiaobei", "feminino", "zh-cn", "z", "Voz feminina em chines mandarim"),
    "zf_xiaoni": kokoro_voice("zf_xiaoni", "Xiaoni", "feminino", "zh-cn", "z", "Voz feminina em chines mandarim"),
    "zf_xiaoxiao": kokoro_voice("zf_xiaoxiao", "Xiaoxiao", "feminino", "zh-cn", "z", "Voz feminina em chines mandarim"),
    "zf_xiaoyi": kokoro_voice("zf_xiaoyi", "Xiaoyi", "feminino", "zh-cn", "z", "Voz feminina em chines mandarim"),
    "zm_yunjian": kokoro_voice("zm_yunjian", "Yunjian", "masculino", "zh-cn", "z", "Voz masculina em chines mandarim"),
    "zm_yunxi": kokoro_voice("zm_yunxi", "Yunxi", "masculino", "zh-cn", "z", "Voz masculina em chines mandarim"),
    "zm_yunxia": kokoro_voice("zm_yunxia", "Yunxia", "masculino", "zh-cn", "z", "Voz masculina em chines mandarim"),
    "zm_yunyang": kokoro_voice("zm_yunyang", "Yunyang", "masculino", "zh-cn", "z", "Voz masculina em chines mandarim"),
}
