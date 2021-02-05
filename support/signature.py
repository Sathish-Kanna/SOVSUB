import random

from ecdsa import NIST384p
from ecdsa import SigningKey
from ecdsa import VerifyingKey
from Crypto.Hash import SHA256


def key_generator(voter_id):
    t_id = str(voter_id)+str(random.randint(1000, 9999))
    sk = SigningKey.generate(curve=NIST384p)
    vk = sk.verifying_key
    sk_str = sk.to_pem().decode()
    vk_str = vk.to_pem().decode()
    return t_id, sk_str, vk_str


def sign(sk_str, data):
    sk = SigningKey.from_pem(sk_str.encode())
    sig = sk.sign(SHA256.new(str(data).encode()).digest())
    return sig.hex()


def verify(vk_str, data, signature):
    vk = VerifyingKey.from_pem(vk_str.encode())
    return vk.verify(bytes.fromhex(signature), SHA256.new(str(data).encode()).digest())
