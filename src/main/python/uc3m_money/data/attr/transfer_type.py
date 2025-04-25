"""Validates the transfer type"""
from uc3m_money.account_management_exception import AccountManagementException
from src.main.python.uc3m_money.data.attr.attribute import Attribute

class TransferType(Attribute):
    """Class validates the transfer type"""
    def validate(self, transfer_type: str) -> None:
        """
        Validates the transfer type:
        Must be one of ORDINARY, INMEDIATE, URGENT
        """
        if transfer_type.upper() not in ["ORDINARY", "INMEDIATE", "URGENT"]:
            raise AccountManagementException("Invalid transfer type")

    def __init__(self, attr_value):
        """Defines the transfer type validation"""
        super().__init__()
        self._validation_pattern = r"^(ORDINARY|INMEDIATE|URGENT)$"
        self._error_message = "Invalid transfer type"
        self._attr_value = self._validate(str(attr_value).upper())
