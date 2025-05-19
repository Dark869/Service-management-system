import bcrypt

def generate_hash(string: str) -> bytes:
    return bcrypt.hashpw(str(string).encode('utf-8'), bcrypt.gensalt())

def check_hash(string: str, hashed: bytes) -> bool:
    if isinstance(hashed, str):
        hashed = hashed.encode('utf-8')
    return bcrypt.checkpw(string.encode('utf-8'), hashed)
