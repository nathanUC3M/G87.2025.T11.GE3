import re
from uc3m_money.account_management_exception import AccountManagementException
from .attribute import Attribute

class TransferType(Attribute):
    def validate(transfer_type: str) -> None:
        """
        Validates the transfer type:
        Must be one of ORDINARY, INMEDIATE, URGENT
        """
        def __init__(self, attr_value):
           self._validation_pattern = r"(ORDINARY|IMMEDIATE|URGENT)"
           self._error_message = "Invalid transfer type"
           self._attr_value = self._validate(attr_value)