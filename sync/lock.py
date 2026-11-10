"""Criptografa o JSON de dados da TV (AES-GCM, chave derivada da senha por PBKDF2).
A pagina publicada so tem a tela de senha e este bloco cifrado; sem a senha nao se le nenhum numero."""
import os, base64, hashlib, json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ITER = 250000


def encrypt(obj, password, salt_hex):
    salt = bytes.fromhex(salt_hex)
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, ITER, 32)
    iv = os.urandom(12)
    raw = json.dumps(obj, ensure_ascii=False, separators=(',', ':')).encode()
    ct = AESGCM(key).encrypt(iv, raw, None)
    e = lambda x: base64.b64encode(x).decode()
    return {'s': e(salt), 'v': e(iv), 'c': e(ct), 'i': ITER}
