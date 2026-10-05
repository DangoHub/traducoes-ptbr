"""Token counting: tiktoken o200k when installed, otherwise an estimate from the character count."""

try:
    import tiktoken

    _ENCODING = tiktoken.get_encoding("o200k_base")
except Exception:
    _ENCODING = None

CHARS_PER_TOKEN = 3.6


def count_tokens(text):
    if _ENCODING is not None:
        return len(_ENCODING.encode(text, disallowed_special=()))
    return round(len(text) / CHARS_PER_TOKEN)
