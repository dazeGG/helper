from rsa import newkeys, encrypt, decrypt, PrivateKey, PublicKey


def _generate_keys():
    (_public_key, _private_key) = newkeys(1024)
    with open('config/keys/public_key.pem', 'wb') as file:
        file.write(_public_key.save_pkcs1('PEM'))
    with open('config/keys/private_key.pem', 'wb') as file:
        file.write(_private_key.save_pkcs1('PEM'))


def _load_keys() -> (PublicKey, PrivateKey):
    with open('config/keys/public_key.pem', 'rb') as file:
        _public_key = PublicKey.load_pkcs1(file.read())
    with open('config/keys/private_key.pem', 'rb') as file:
        _private_key = PrivateKey.load_pkcs1(file.read())
    return _public_key, _private_key


def _encrypt(_text: str, _key: PublicKey | PrivateKey) -> bytes:
    return encrypt(_text.encode('ascii'), _key)


def _decrypt(_crypted_text: bytes, _key: PublicKey | PrivateKey) -> str | bool:
    return decrypt(_crypted_text, _key).decode('ascii')
