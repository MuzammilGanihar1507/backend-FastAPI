# generate_secret.py
import base64
import secrets

def generate_hs256_secret(fmt: str = "urlsafe") -> str:
    """
    Returns a 32-byte (256-bit) secret string for HS256.
    fmt: "urlsafe" (default) or "hex" or "base64"
    """
    key_bytes = secrets.token_bytes(32)  # 32 bytes = 256 bits

    # urlsafe base64 without padding (‘=’), great for .env / headers
    print(base64.urlsafe_b64encode(key_bytes).rstrip(b"=").decode("utf-8"))

generate_hs256_secret()