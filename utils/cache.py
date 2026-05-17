import hashlib
import diskcache

# one cache instance
cache = diskcache.Cache("./cache")

def get_file_hash(file) -> str:
    content = file.read()
    file.seek(0)
    return hashlib.md5(content).hexdigest()

def get_text_hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()

def make_key(*args) -> str:
    combined = "_".join([str(a) for a in args])
    return hashlib.md5(combined.encode()).hexdigest()