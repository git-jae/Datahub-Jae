import re

def parse_text_input(text: str) -> list:
    if not text or not text.strip():
        return []
    return [t.strip() for t in re.sub(r"[,\n\r]+", " ", text).split() if t.strip()]
