from rsa import newkeys, encrypt, decrypt, PrivateKey, PublicKey
from bot.config import collection


def _generate_keys():
    (_public_key, _private_key) = newkeys(4096)
    keys = collection.find_one({'_id': 'keys'})['keys']
    keys['public_key'], keys['private_key'] = _public_key.save_pkcs1('PEM'), _private_key.save_pkcs1('PEM')
    collection.update_one({'_id': 'keys'}, {'$set': {'keys': keys}})


def _load_keys() -> (PublicKey, PrivateKey):
    keys = collection.find_one({'_id': 'keys'})['keys']
    _public_key = PublicKey.load_pkcs1(keys['public_key'])
    _private_key = PrivateKey.load_pkcs1(keys['private_key'])
    return _public_key, _private_key


def _encrypt(_text: str, _key: PublicKey) -> bytes:
    return encrypt(_text.encode('ascii'), _key)


def _decrypt(_crypted_text: bytes, _key: PrivateKey) -> str | bool:
    return decrypt(_crypted_text, _key).decode('ascii')
