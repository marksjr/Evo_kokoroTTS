# Evo KokoroTTS

Local **multilingual Text-to-Speech API** built with **Kokoro-82M** plus complementary **Edge TTS** voices.

It generates high-quality audio in MP3 or WAV, supports real-time streaming, exposes a FastAPI REST API, and includes a local web UI in English.

---

## Highlights

- **54 official Kokoro voices included locally**
- **6 extra Edge TTS voices** for German and child-like Brazilian presets
- **10 language options in the catalog**
  - `pt-br`, `en-us`, `en-gb`, `es-es`, `fr-fr`, `ja-jp`, `zh-cn`, `hi-in`, `it-it`, `de-de`
- **Automatic Kokoro / Edge routing** based on the selected voice
- **English web UI**
- **MP3 and WAV output**
- **Real-time MP3 streaming**
- **Automatic voice availability validation**
- **CUDA or CPU auto-detection**
- **Local bootstrap installer** via `install.bat`

---

## Included Voice Coverage

This repository now includes:

- **All 54 official Kokoro-82M v1.0 voice files** in `models/kokoro_voices/voices/`
- **6 Edge TTS voices** registered in the API catalog:
  - `de_f_katja`
  - `de_m_conrad`
  - `de_f_leni`
  - `de_m_jonas`
  - `pt_f_menina`
  - `pt_m_menino`

The API marks each voice as available or unavailable, and rejects requests for missing local Kokoro voice files before synthesis starts.

---

## Installation

### Requirements

- **Windows 10/11** (64-bit)
- **espeak-ng** required for Kokoro synthesis

The installer already handles:

- Python setup or reuse of an existing Python installation
- `ffmpeg`
- PyTorch CPU or CUDA build
- Python dependencies from `requirements.txt`

Supported `espeak-ng` setups:

- installed globally and available in `PATH`
- portable copy in `.\espeak-ng\`
- portable copy in `.\espeak-ng\command_line\`

### Quick Start

```powershell
git clone https://github.com/marksjr/EvoKokoroTTS.git
cd EvoKokoroTTS
install.bat
run-kokoro.bat
```

After startup, open:

- Web UI: `http://localhost:8880`
- Swagger docs: `http://localhost:8880/docs`
- Extended docs: `http://localhost:8880/doc.html`

---

## Web Interface

The local UI includes:

- text input up to **10,000 characters**
- language and voice selection
- speed and pitch controls
- MP3 / WAV format toggle
- full generation and streaming actions
- live generation timer
- inline availability state for voices
- in-browser playback and download

Top-right status shows:

- **Online / Offline**
- **GPU (CUDA)** or **CPU**

---

## API

### Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/health` | API status, device, model state |
| `GET` | `/languages` | Available language catalog |
| `GET` | `/voices` | Full voice catalog with availability |
| `POST` | `/tts` | Full audio generation (`mp3` or `wav`) |
| `POST` | `/tts/stream` | Real-time MP3 streaming |

### `POST /tts`

```json
{
  "text": "Hello from Evo KokoroTTS.",
  "voice": "af_bella",
  "speed": 1.0,
  "pitch": 0,
  "format": "mp3"
}
```

### `POST /tts/stream`

```json
{
  "text": "This is a live streaming synthesis test.",
  "voice": "pm_alex",
  "speed": 1.0,
  "pitch": 0
}
```

Voice validation now checks:

- voice exists in the catalog
- language is supported
- local Kokoro `.pt` file exists when required

---

## Example cURL Commands

```bash
# Health
curl http://localhost:8880/health

# Languages
curl http://localhost:8880/languages

# Voices
curl http://localhost:8880/voices

# Minimal MP3
curl -X POST http://localhost:8880/tts \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Hello world.\"}" \
  --output audio.mp3

# Brazilian Portuguese Kokoro
curl -X POST http://localhost:8880/tts \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Ola. Este e um teste em portugues.\",\"voice\":\"pf_dora\",\"format\":\"mp3\"}" \
  --output pt.mp3

# British English Kokoro
curl -X POST http://localhost:8880/tts \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Hello. This is a British English test.\",\"voice\":\"bf_alice\",\"format\":\"mp3\"}" \
  --output en_gb.mp3

# Chinese Kokoro
curl -X POST http://localhost:8880/tts \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"你好，这是一个中文测试。\",\"voice\":\"zf_xiaoxiao\",\"format\":\"mp3\"}" \
  --output zh.mp3

# Edge voice with pitch
curl -X POST http://localhost:8880/tts \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Testing Edge voice pitch.\",\"voice\":\"pt_f_menina\",\"speed\":1.08,\"pitch\":46}" \
  --output edge.mp3

# WAV
curl -X POST http://localhost:8880/tts \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Uncompressed output.\",\"format\":\"wav\"}" \
  --output audio.wav

# Streaming
curl -X POST http://localhost:8880/tts/stream \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Streaming test in real time.\"}" \
  --output stream.mp3
```

---

## Language and Voice Notes

- `en-us` covers the American English Kokoro voices
- `en-gb` covers the British English Kokoro voices
- `de-de` currently uses the extra Edge TTS voices
- `pt-br` includes both official Kokoro voices and two extra Edge child-like presets
- `zh-cn` requires the Chinese text-processing dependencies already listed in `requirements.txt`

Use `GET /voices` to inspect the full catalog returned by the running instance.

---

## Dependencies

Current Python dependencies include:

- `fastapi`
- `uvicorn[standard]`
- `kokoro`
- `torch`
- `edge-tts`
- `soundfile`
- `numpy`
- `pydub`
- `ordered-set`
- `pypinyin`
- `cn2an`
- `jieba`

The last four packages are required so the Chinese Kokoro pipeline can load correctly.

---

## Technical Specs

| Item | Value |
|------|-------|
| Model | Kokoro-82M |
| Kokoro sample rate | 24 kHz |
| MP3 bitrate (full) | 320 kbps |
| MP3 bitrate (streaming) | 256 kbps |
| WAV | 16-bit PCM mono |
| Port | `8880` |
| Device | CUDA if available, otherwise CPU |
| Max text length | 10,000 characters |
| Speed range | `0.5x` to `2.0x` |
| Concurrent Kokoro workers | 4 |

---

## Project Structure

```text
EvoKokoroTTS/
├── install.bat
├── run-kokoro.bat
├── start.py
├── requirements.txt
├── doc.html
├── README.md
├── models/
│   └── kokoro_voices/
│       └── voices/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── routes.py
│   ├── core/
│   │   └── config.py
│   ├── engines/
│   │   ├── edge_engine.py
│   │   └── kokoro_engine.py
│   ├── models/
│   │   └── schemas.py
│   ├── services/
│   │   └── tts_service.py
│   ├── static/
│   │   └── index.html
│   └── utils/
│       ├── audio.py
│       └── text.py
```

---

## License

MIT
