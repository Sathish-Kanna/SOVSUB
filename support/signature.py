import random

from ecies import encrypt
from ecies import decrypt
from ecies.utils import generate_eth_key
from Crypto.Hash import SHA256


def key_generator(voter_id):
    t_id = SHA256.new(voter_id+str(random.randint(1000, 9999)))
    eth_k = generate_eth_key()
    sk_hex = eth_k.to_hex()  # hex string
    pk_hex = eth_k.public_key.to_hex()  # hex string
    return t_id, sk_hex, pk_hex


def sign(privatekey, data):
    return encrypt(privatekey, SHA256.new(data))


def verify(publickey, data, sign):
    return decrypt(publickey, sign) == SHA256.new(data)
