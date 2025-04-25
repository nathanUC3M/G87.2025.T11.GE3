"""Defines the transfer concept"""
from src.main.python.uc3m_money.data.attr.attribute import Attribute

class Concept(Attribute):
    """Defines the transfer concept"""
    def __init__(self, attr_value: str):
        """
        Validates the transfer concept:
        - Length between 10 and 30 characters
        - Only letters and spaces
        - At least two words
        """
        super().__init__()
        self._validation_pattern = r"^(?=.{10,30}$)([A-Za-z]+(\s[A-Za-z]+)+)$"
        self._error_message = "Invalid concept format"
        self._attr_value = self._validate(attr_value)
