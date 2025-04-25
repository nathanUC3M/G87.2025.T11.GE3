"""TransferType defines the transfer type"""
from uc3m_money.data.attr.attribute import Attribute

class TransferType(Attribute):
    """Consolidates and defines transfer type"""
    def validate(self) -> None:
        """
        Validates the transfer type:
        Must be one of ORDINARY, INMEDIATE, URGENT
        """
        def __init__(self, attr_value):
            self._validation_pattern = r"(ORDINARY|IMMEDIATE|URGENT)"
            self._error_message = "Invalid transfer type"
            self._attr_value = self._validate(attr_value)
