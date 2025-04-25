from src.main.python.uc3m_money.account_management_exception import AccountManagementException
from src.main.python.uc3m_money.data.attr.attribute import Attribute
import re


class IbanCode(Attribute):
    def __init__(self, attr_value):
        super().__init__()
        self._validation_pattern = r"^ES\d{22}$"  # Accept only ES and exactly 22 digits
        self._error_message = "Invalid IBAN format"
        self._attr_value = self._validate(attr_value)

    def _validate(self, attr_value):
        attr_value = str(attr_value).replace(" ", "").upper()
        if not re.fullmatch(self._validation_pattern, attr_value):
            raise AccountManagementException(self._error_message)
        iban = attr_value
        original_code = iban[2:4]
        iban_rearranged = iban[4:] + iban[:4]
        iban_numeric = ""
        for c in iban_rearranged:
            if c.isdigit():
                iban_numeric += c
            else:
                iban_numeric += str(ord(c) - 55)  # 'A'->10 ... 'Z'->35
        try:
            int_iban = int(iban_numeric)
        except Exception:
            raise AccountManagementException(self._error_message)

        if int_iban % 97 != 1:
            raise AccountManagementException("Invalid IBAN control digit")

        return attr_value