import re
from astroid import Attribute
from uc3m_money import AccountManagementException

class AttributeIban(Attribute):

    def __init__(self, iban):
        self.value = self.validate_iban(iban)



    @staticmethod
    def validate_iban(modified_iban: str):
        """
    Calcula el dígito de control de un IBAN español.

    Args:
        modified_iban (str): El IBAN sin los dos últimos dígitos (dígito de control).

    Returns:
        str: El dígito de control calculado.
        """
        country_code_check = re.compile(r"^ES[0-9]{22}")
        valid_iban = country_code_check.fullmatch(modified_iban)
        if not valid_iban:
            raise AccountManagementException("Invalid IBAN format")
        iban = modified_iban
        original_code = iban[2:4]
        # replacing the control
        iban = iban[:2] + "00" + iban[4:]
        iban = iban[4:] + iban[:4]

        # Convertir el IBAN en una cadena numérica, reemplazando letras por números
        iban = (iban.replace('A', '10').replace('B', '11').
                replace('C', '12').replace('D', '13').replace('E', '14').
                replace('F', '15'))
        iban = (iban.replace('G', '16').replace('H', '17').
                replace('I', '18').replace('J', '19').replace('K', '20').
                replace('L', '21'))
        iban = (iban.replace('M', '22').replace('N', '23').
                replace('O', '24').replace('P', '25').replace('Q', '26').
                replace('R', '27'))
        iban = (iban.replace('S', '28').replace('T', '29').replace('U', '30').
                replace('V', '31').replace('W', '32').replace('X', '33'))
        iban = iban.replace('Y', '34').replace('Z', '35')

        # Mover los cuatro primeros caracteres al final

        # Convertir la cadena en un número entero
        iban_integer = int(iban)

        # Calcular el módulo 97
        iban_mod = iban_integer % 97

        # Calcular el dígito de control (97 menos el módulo)
        valid_check_digits = 98 - iban_mod

        if int(original_code) != valid_check_digits:
            # print(valid_check_digits)
            raise AccountManagementException("Invalid IBAN control digit")
        return modified_iban
