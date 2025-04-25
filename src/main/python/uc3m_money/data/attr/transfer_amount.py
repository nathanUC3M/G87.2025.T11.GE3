from uc3m_money.account_management_exception import AccountManagementException
from uc3m_money.data.attr.attribute import Attribute

class TransferAmount(Attribute):
    def __init__(self, attr_value):
        """
        Validates the transfer amount:
        - Must be numeric
        - Max two decimal places
        - Between 10.00 and 10000.00 inclusive
        """
        # pattern matches numbers with optional decimal part up to 2 digits
        self._validation_pattern = r"^\d+(?:\.\d{1,2})?$"
        self._error_message = "Invalid transfer amount"
        raw = self._validate(str(attr_value))
        try:
            value = float(raw)
        except ValueError:
            raise AccountManagementException(self._error_message)
        if value < 10 or value > 10000:
            raise AccountManagementException(self._error_message)
        # store numeric as string or keep as raw
        self._attr_value = value