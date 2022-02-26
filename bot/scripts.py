from random import randint


def generate_password(x: int, alphabet: str) -> str:
    password = ''
    len_alphabet = len(alphabet) - 1
    for i in range(x):
        password += alphabet[randint(0, len_alphabet)]
    return password
