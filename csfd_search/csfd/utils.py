import unicodedata

from functools import lru_cache

@lru_cache
def normalize(text):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', text)
        if not unicodedata.combining(c)
    ).lower()