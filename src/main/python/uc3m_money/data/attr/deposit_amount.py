import re
from uc3m_money.account_management_exception import AccountManagementException

class DepositAmountValidator:
    @staticmethod
    def validate(deposit_amount: str) -> float:
        """
        Validates the deposit amount string:
        - Format "EUR ####.##"
        - Value > 0
        Returns the numeric amount
        """
        pattern = re.compile(r"^EUR\s[0-9]{1,}\.[0-9]{2}$")
        if not pattern.fullmatch(deposit_amount):
            raise AccountManagementException("Error - Invalid deposit amount")
        value = float(deposit_amount.split()[1])
        if value <= 0:
            raise AccountManagementException("Error - Deposit must be greater than 0")
        return value