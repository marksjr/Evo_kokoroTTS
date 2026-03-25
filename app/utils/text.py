import re
import unicodedata

from app.core.config import CHUNK_ABSOLUTE_MAX_CHARS, CHUNK_TARGET_MAX_CHARS, CHUNK_TARGET_MIN_CHARS


def normalize_unicode(text: str) -> str:
    """Normaliza texto para NFC (forma composta).
    Garante que 'ã' seja um único caractere e não 'a' + '~' separados.
    Essencial para consistência na síntese de pt-BR."""
    return unicodedata.normalize("NFC", text)


def normalize_special_chars(text: str) -> str:
    """Normaliza caracteres tipográficos para equivalentes simples."""
    text = re.sub(r'[\u201C\u201D\u201E\u201F\u00AB\u00BB]', '"', text)
    text = re.sub(r'[\u2018\u2019\u201A\u201B]', "'", text)
    text = re.sub(r"\s*[\u2013\u2014]\s*", ", ", text)
    text = text.replace("\u2026", "...")
    text = re.sub(r"[\u00A0\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200A\u202F\u205F]", " ", text)
    return text


def preprocess_text_ptbr(text: str) -> str:
    """Pré-processamento de texto para pt-BR.
    Normaliza Unicode, expande abreviações e limpa formatação."""
    text = text.strip()
    text = normalize_unicode(text)
    text = normalize_special_chars(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    replacements = {
        r"\bDr\.\b": "Doutor",
        r"\bDra\.\b": "Doutora",
        r"\bSr\.\b": "Senhor",
        r"\bSra\.\b": "Senhora",
        r"\bSrta\.\b": "Senhorita",
        r"\bProf\.\b": "Professor",
        r"\bProfa\.\b": "Professora",
        r"\bEng\.\b": "Engenheiro",
        r"\bAdv\.\b": "Advogado",
        r"\bAv\.\b": "Avenida",
        r"\bR\.\b": "Rua",
        r"\bArt\.\b": "Artigo",
        r"\barts\.\b": "artigos",
        r"\btel\.\b": "telefone",
        r"\bcel\.\b": "celular",
        r"\bLtda\.\b": "Limitada",
        r"\bCia\.\b": "Companhia",
        r"\bS\.A\.\b": "Sociedade Anônima",
        r"\bDepto\.\b": "Departamento",
        r"\bDept\.\b": "Departamento",
        r"\bMin\.\b": "Ministério",
        r"\bGov\.\b": "Governo",
        r"\betc\.\b": "etcétera",
        r"\bpág\.\b": "página",
        r"\bpágs\.\b": "páginas",
        r"\bvol\.\b": "volume",
        r"\bcap\.\b": "capítulo",
        r"\bex\.\b": "exemplo",
        r"\bobs\.\b": "observação",
        r"\baprox\.\b": "aproximadamente",
        r"\bqtd\.\b": "quantidade",
        r"\bqtde\.\b": "quantidade",
    }
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    text = re.sub(r"\b[nN][°º]\s*", "número ", text)

    ordinals_masc = {
        "1": "primeiro",
        "2": "segundo",
        "3": "terceiro",
        "4": "quarto",
        "5": "quinto",
        "6": "sexto",
        "7": "sétimo",
        "8": "oitavo",
        "9": "nono",
        "10": "décimo",
    }
    ordinals_fem = {
        "1": "primeira",
        "2": "segunda",
        "3": "terceira",
        "4": "quarta",
        "5": "quinta",
        "6": "sexta",
        "7": "sétima",
        "8": "oitava",
        "9": "nona",
        "10": "décima",
    }
    for num, word in ordinals_masc.items():
        text = re.sub(rf"\b{num}[ºo°]\b", word, text)
    for num, word in ordinals_fem.items():
        text = re.sub(rf"\b{num}[ªa]\b", word, text)

    text = re.sub(r"\s*&\s*", " e ", text)
    text = re.sub(r"R\$\s*(\d)", r"\1 reais", text)
    text = re.sub(r"US\$\s*(\d)", r"\1 dólares", text)
    text = re.sub(r"€\s*(\d)", r"\1 euros", text)
    text = re.sub(r"(\d)\s*%", r"\1 por cento", text)
    text = re.sub(r"(\d+)[°º]", r"\1o", text)
    text = re.sub(r"(\d+)ª", r"\1a", text)
    text = re.sub(r"  +", " ", text)

    return text


def preprocess_text(text: str, language: str) -> str:
    """Pré-processamento genérico com regra especializada para pt-BR."""
    if language == "pt-br":
        return preprocess_text_ptbr(text)

    text = text.strip()
    text = normalize_unicode(text)
    text = normalize_special_chars(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def split_into_sentences(text: str) -> list[str]:
    """Divide texto em sentenças respeitando regras pt-BR.
    Lida com reticências (...), pontuação combinada (?!), e quebras de linha."""
    text = re.sub(r"\.{3}", "\u2026", text)
    parts = re.split(r"(?<=[.!?;:\u2026。！？])\s*", text)
    sentences = []
    for part in parts:
        part = part.replace("\u2026", "...")
        sub_parts = re.split(r"\n+", part)
        sentences.extend(s.strip() for s in sub_parts if s.strip())
    return sentences


def chunk_text(text: str) -> list[str]:
    """Agrupa sentenças em chunks respeitando limites do modelo.
    Chunks menores melhoram qualidade; muito pequenos perdem contexto prosódico."""
    sentences = split_into_sentences(text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(sentence) > CHUNK_ABSOLUTE_MAX_CHARS:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            sub_parts = re.split(r"(?<=,)\s+", sentence)
            sub_chunk = ""
            for sp in sub_parts:
                if len(sub_chunk) + len(sp) + 1 <= CHUNK_TARGET_MAX_CHARS:
                    sub_chunk = f"{sub_chunk} {sp}".strip() if sub_chunk else sp
                else:
                    if sub_chunk:
                        chunks.append(sub_chunk.strip())
                    sub_chunk = sp
            if sub_chunk:
                chunks.append(sub_chunk.strip())
            continue

        candidate = f"{current_chunk} {sentence}".strip() if current_chunk else sentence

        if len(candidate) <= CHUNK_TARGET_MAX_CHARS:
            current_chunk = candidate
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
