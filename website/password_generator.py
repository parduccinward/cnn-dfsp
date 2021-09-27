import string
import random


# caracteres para generar una contraseña
alphabets = list(string.ascii_letters)
digits = list(string.digits)
special_characters = list("!@#$%^&*()")
characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")


def generate_random_password():
    # longitud de la contraseña
    length = 10

    # numero de caracteres obligatorios
    alphabets_character = 4
    digits_character = 4
    special_characters_count = 2

    # inicializando la contraseña
    password = []

    # agregando del alfabeto
    for i in range(alphabets_character):
        password.append(random.choice(alphabets))

    # agregando numeros
    for i in range(digits_character):
        password.append(random.choice(digits))

    # agregando caracteres especiales
    for i in range(special_characters_count):
        password.append(random.choice(special_characters))

    # mezclando al azar la contraseña
    random.shuffle(password)

    # convirtiendo la contraseña a un string
    # imprimiendo la contraseña
    return ("".join(password))
