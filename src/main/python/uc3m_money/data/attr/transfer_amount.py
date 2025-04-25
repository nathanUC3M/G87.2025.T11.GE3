"""
Defines the TransferAmount attribute class for validating and storing a transfer amount.
"""

from uc3m_money.account_management_exception import AccountManagementException
from uc3m_money.data.attr.attribute import Attribute

class TransferAmount(Attribute):
    """
    Attribute class for validating and representing a transfer amount.

    Validates that the value is numeric, has at most two decimal places,
    and is within the allowed range (10.00 to 10,000.00).
    """
    def __init__(self, attr_value):
        """
        Initialize TransferAmount and validate the input value.
        """
        super().__init__()
        self._validation_pattern = r"^\d+(?:\.\d{1,2})?$"
        self._error_message = "Invalid transfer amount"
        raw = self._validate(str(attr_value))
        try:
            value = float(raw)
        except ValueError as exc:
            raise AccountManagementException(self._error_message) from exc
        if value < 10 or value > 10000:
            raise AccountManagementException(self._error_message)
        self._attr_value = value
