"""Validates the deposit amount string"""
from src.main.python.uc3m_money.account_management_exception import AccountManagementException
from src.main.python.uc3m_money.data.attr.attribute import Attribute

class DepositAmount(Attribute):
    """Validates the deposit amount string"""
    def __init__(self, attr_value: str):
        """
        Validates the deposit amount string:
        - Format "EUR ####.##"
        - Value greater than 0
        """
        super().__init__()
        self._validation_pattern = r"^EUR\s\d+\.\d{2}$"
        self._error_message = "Error - Invalid deposit amount"
        raw = self._validate(attr_value)
        # extract numeric part
        try:
            value = float(raw.split()[1])
        except (IndexError, ValueError) as exc:
            raise AccountManagementException(self._error_message) from exc
        if value <= 0:
            raise AccountManagementException("Error - Deposit must be greater than 0")
        self._attr_value = value
