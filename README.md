# Evo KokoroTTS

API local de **Text-to-Speech multilingue** usando **Kokoro-82M** e vozes complementares via **Edge TTS**.

Converta texto em audio de alta qualidade com multiplas vozes, controle de velocidade e streaming em tempo real. Interface web inclusa, sem necessidade de conhecimento tecnico.

---

## Recursos

- **Multilingue** - `pt-br`, `en-us`, `es-es`, `fr-fr`, `ja-jp` e `de-de`
- **Kokoro + Edge TTS** - Seleciona a engine automaticamente conforme a voz
- **Interface web** - Abre no navegador local, pronta para uso
- **API REST** completa com documentacao Swagger interativa
- **Streaming em tempo real** - Receba o audio enquanto esta sendo gerado
- **Deteccao automatica GPU/CPU** - Usa placa de video NVIDIA se disponivel
- **Bootstrap local** - `install.bat` prepara Python, ffmpeg, PyTorch e dependencias
- **Formato portatil** - Tambem aceita `ffmpeg` e `espeak-ng` dentro da pasta do projeto
- **Formatos MP3 e WAV** - MP3 a 320kbps ou WAV 16-bit PCM
- **Otimizado para pt-BR** - Pre-processamento de acentos, abreviacoes, moedas, ordinais

---

## Instalacao

### Requisitos

- **Windows 10/11** (64-bit)
- **espeak-ng** - necessario para a sintese Kokoro

O instalador ja cuida de:
- Python (ou usa o Python existente)
- ffmpeg
- PyTorch CPU ou CUDA
- dependencias Python do projeto

Para o `espeak-ng`, ha dois jeitos suportados:
- instalar no Windows e adicionar ao `PATH`
- usar de forma portable extraindo em `.\espeak-ng\` ou `.\espeak-ng\command_line\`

### Passo a passo

```
1. Baixe ou clone o repositorio
   git clone https://github.com/marksjr/Evo_kokoroTTS.git

2. Prepare o espeak-ng
   - Opcao A: instale no Windows a partir de https://github.com/espeak-ng/espeak-ng/releases
   - Opcao B: extraia uma copia portable em `.\espeak-ng\` ou `.\espeak-ng\command_line\`

3. Execute o instalador (duplo-clique)
   install.bat

4. Inicie o servidor (duplo-clique)
   run-kokoro.bat
```

O instalador detecta automaticamente:
- Se voce tem **Python** instalado (senao, baixa Python Embedded automaticamente)
- Se voce tem **ffmpeg** (senao, baixa automaticamente)
- Se voce tem **GPU NVIDIA** (instala PyTorch CUDA) ou **apenas CPU** (instala versao leve)
- Se `ffmpeg` e `espeak-ng` estao no sistema ou em pastas locais do projeto

Apos iniciar com `run-kokoro.bat`, a interface web abre automaticamente no navegador.

---

## Interface Web

Acesse `http://localhost:8880` apos iniciar o servidor.

| Funcao | Descricao |
|--------|-----------|
| **Texto** | Digite ou cole ate 10.000 caracteres |
| **Idioma** | Escolha entre os idiomas disponiveis no catalogo |
| **Voz** | Escolha uma voz compativel com o idioma selecionado |
| **Velocidade** | De 0.5x (lenta) a 2.0x (rapida) |
| **Pitch** | Ajuste fino para vozes Edge TTS |
| **Formato** | MP3 (320kbps) ou WAV (PCM 16-bit) |
| **Gerar Audio** | Gera o audio completo e reproduz |
| **Streaming** | Gera e envia em tempo real |
| **Download** | Baixa o arquivo gerado como `audio.mp3` ou `audio.wav` |

O status no canto superior direito mostra:
- **Online / Offline** - Se a API esta rodando
- **GPU (CUDA)** ou **CPU** - Qual hardware esta sendo usado

---

## API REST

Documentacao interativa disponivel em `http://localhost:8880/docs` (Swagger UI).

### Endpoints

| Metodo | Rota | Descricao |
|--------|------|-----------|
| `GET` | `/health` | Status da API (online, device, modelo) |
| `GET` | `/languages` | Lista idiomas disponiveis |
| `GET` | `/voices` | Lista vozes disponiveis |
| `POST` | `/tts` | Gera audio completo (MP3 ou WAV) |
| `POST` | `/tts/stream` | Streaming de audio em tempo real |

### POST /tts - Gerar audio

```json
{
  "text": "Ola! Meu nome e Dora.",
  "voice": "pf_dora",
  "speed": 1.0,
  "format": "mp3"
}
```

| Campo | Tipo | Obrigatorio | Padrao | Descricao |
|-------|------|:-----------:|--------|-----------|
| `text` | string | **Sim** | - | Texto para sintetizar (1 a 10.000 caracteres) |
| `voice` | string | Nao | `pf_dora` | ID da voz. Use `GET /voices` para listar o catalogo completo |
| `speed` | float | Nao | `1.0` | Velocidade: `0.5` (lenta) a `2.0` (rapida) |
| `pitch` | int | Nao | `0` | Ajuste de pitch em Hz para vozes Edge (`-80` a `80`) |
| `format` | string | Nao | `mp3` | `mp3` (320kbps) ou `wav` (PCM 16-bit) |

### POST /tts/stream - Streaming

```json
{
  "text": "Texto longo para streaming em tempo real.",
  "voice": "pm_alex",
  "speed": 1.2
}
```

| Campo | Tipo | Obrigatorio | Padrao | Descricao |
|-------|------|:-----------:|--------|-----------|
| `text` | string | **Sim** | - | Texto para sintetizar (1 a 10.000 caracteres) |
| `voice` | string | Nao | `pf_dora` | ID da voz. Use `GET /voices` para listar o catalogo completo |
| `speed` | float | Nao | `1.0` | Velocidade: `0.5` a `2.0` |
| `pitch` | int | Nao | `0` | Ajuste de pitch em Hz para vozes Edge (`-80` a `80`) |

Resposta: streaming MP3 a 256kbps (chunked transfer).

---

## Exemplos de uso via cURL

```bash
# Verificar status
curl http://localhost:8880/health

# Listar idiomas
curl http://localhost:8880/languages

# Listar vozes
curl http://localhost:8880/voices

# Gerar MP3 (minimo)
curl -X POST http://localhost:8880/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"Ola, mundo!"}' \
  --output audio.mp3

# Gerar em ingles
curl -X POST http://localhost:8880/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello from Evo KokoroTTS.","voice":"af_bella","speed":1.0,"format":"mp3"}' \
  --output english.mp3

# Gerar com voz Edge e pitch
curl -X POST http://localhost:8880/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"Testando a API.","voice":"pt_f_menina","speed":1.08,"pitch":46}' \
  --output audio.mp3

# Gerar WAV
curl -X POST http://localhost:8880/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"Audio sem compressao.","format":"wav"}' \
  --output audio.wav

# Streaming
curl -X POST http://localhost:8880/tts/stream \
  -H "Content-Type: application/json" \
  -d '{"text":"Streaming em tempo real."}' \
  --output stream.mp3
```

---

## Idiomas e vozes

Use `GET /languages` para ver os idiomas ativos e `GET /voices` para obter o catalogo completo. O idioma e definido pela `voice` escolhida.

| Idioma | Exemplos de vozes |
|--------|-------------------|
| `pt-br` | `pf_dora`, `pm_alex`, `pm_santa`, `pt_f_menina`, `pt_m_menino` |
| `en-us` | `af_bella`, `am_adam`, `bf_emma`, `bm_george` |
| `es-es` | `ef_dora`, `em_alex`, `em_santa` |
| `fr-fr` | `ff_siwis` |
| `ja-jp` | `jf_alpha`, `jm_kumo` |
| `de-de` | `de_f_katja`, `de_m_conrad`, `de_f_leni`, `de_m_jonas` |

---

## Documentacao completa

Acesse `http://localhost:8880/doc.html` para a documentacao detalhada com:

- Especificacoes tecnicas (sample rate, bitrate, formatos)
- Pipeline de processamento completo
- Pre-processamento automatico de pt-BR
- Como selecionar outros idiomas
- Exemplos em cURL, JavaScript, Python e PHP
- Codigos de erro e limites

---

## Pre-processamento automatico pt-BR

A API trata automaticamente caracteres especiais e abreviacoes do portugues:

| Entrada | Convertido para |
|---------|-----------------|
| `Dr.` / `Dra.` / `Sr.` / `Sra.` | Doutor / Doutora / Senhor / Senhora |
| `Prof.` / `Eng.` / `Adv.` | Professor / Engenheiro / Advogado |
| `Av.` / `R.` / `n.` | Avenida / Rua / numero |
| `Ltda.` / `Cia.` / `S.A.` | Limitada / Companhia / Sociedade Anonima |
| `R$ 50` / `US$ 100` / `E 200` | 50 reais / 100 dolares / 200 euros |
| `30%` | 30 por cento |
| `1o` a `10o` / `1a` a `10a` | primeiro a decimo / primeira a decima |
| `&` | e |
| Aspas tipograficas, travessoes | Convertidos automaticamente |
| Acentos (a, c, e, o, u) | Normalizacao Unicode NFC |

---

## Especificacoes tecnicas

| Spec | Valor |
|------|-------|
| Modelo | Kokoro-82M (82M parametros) |
| Sample Rate | 24 kHz |
| MP3 Bitrate (completo) | 320 kbps |
| MP3 Bitrate (streaming) | 256 kbps |
| WAV | 16-bit PCM, mono |
| Porta | 8880 |
| Device | Auto (CUDA se disponivel, senao CPU) |
| Texto maximo | 10.000 caracteres |
| Velocidade | 0.5x a 2.0x |
| Requisicoes simultaneas | 4 |

---

## Estrutura do projeto

```
Evo_kokoroTTS/
├── install.bat           # Instalador automatico
├── run-kokoro.bat        # Iniciar servidor
├── requirements.txt      # Dependencias Python
├── start.py              # Entry point
├── doc.html              # Documentacao detalhada
│
└── app/
    ├── main.py           # FastAPI app + interface web
    ├── api/
    │   └── routes.py     # Endpoints da API
    ├── core/
    │   └── config.py     # Configuracoes (vozes, audio, servidor)
    ├── engines/
    │   └── kokoro_engine.py  # Motor de sintese Kokoro-82M
    ├── models/
    │   └── schemas.py    # Schemas Pydantic (request/response)
    ├── services/
    │   └── tts_service.py    # Servico TTS (async + thread pool)
    ├── static/
    │   └── index.html    # Interface web
    └── utils/
        ├── audio.py      # Processamento de audio (crossfade, normalize, encode)
        └── text.py       # Pre-processamento de texto pt-BR
```

---

## Licenca

MIT
