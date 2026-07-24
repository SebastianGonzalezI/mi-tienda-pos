import re


def validar_cedula_ecuador(cedula):
    if not cedula or len(cedula) != 10:
        return False
    try:
        coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        total = 0
        for i in range(9):
            digito = int(cedula[i]) * coeficientes[i]
            if digito >= 10:
                digito -= 9
            total += digito
        digito_verificador = int(cedula[9])
        return (total % 10 == 0 and digito_verificador == 0) or (10 - total % 10 == digito_verificador)
    except (ValueError, IndexError):
        return False


def validar_email(email):
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, email)) if email else False


def validar_telefono(telefono):
    patron = r'^0[9][0-9]{8}$'
    return bool(re.match(patron, telefono)) if telefono else False


def validar_no_vacio(texto):
    return bool(texto and texto.strip())


def validar_precio_positivo(precio):
    try:
        return float(precio) > 0
    except (ValueError, TypeError):
        return False


def validar_cantidad_positiva(cantidad):
    try:
        return int(cantidad) > 0
    except (ValueError, TypeError):
        return False
