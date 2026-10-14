"""Découpage de documents Markdown en passages (chunks) par paragraphes, avec taille maximale."""
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class Chunk:
    source: str
    index: int
    text: str

    @property
    def ref(self) -> str:
        return f"{self.source}#{self.index}"


def split_text(text: str, max_chars: int = 500) -> List[str]:
    """Regroupe des paragraphes entiers jusqu'à max_chars ; un paragraphe trop long est coupé par phrases."""
    pieces: List[str] = []
    for para in (p.strip() for p in text.split("\n\n") if p.strip()):
        if len(para) <= max_chars:
            pieces.append(para)
            continue
        cur = ""
        for sent in para.replace("\n", " ").split(". "):
            sent = sent if sent.endswith(".") else sent + "."
            if cur and len(cur) + len(sent) + 1 > max_chars:
                pieces.append(cur)
                cur = sent
            else:
                cur = f"{cur} {sent}".strip()
        if cur:
            pieces.append(cur)
    return pieces


def load_chunks(docs_dir: str, max_chars: int = 500) -> List[Chunk]:
    chunks: List[Chunk] = []
    for path in sorted(Path(docs_dir).glob("*.md")):
        for i, piece in enumerate(split_text(path.read_text(encoding="utf-8"), max_chars)):
            chunks.append(Chunk(path.name, i, piece))
    return chunks
