from uc3m_money.account_management_exception import AccountManagementException

class TransferAmountValidator:
    @staticmethod
    def validate(amount) -> float:
        """
        Validates the transfer amount:
        - Must be numeric
        - Max two decimal places
        - Between 10.00 and 10000.00 inclusive
        Returns the float value if valid
        """
        try:
            value = float(amount)
        except (ValueError, TypeError):
            raise AccountManagementException("Invalid transfer amount")
        # Check decimals
        parts = str(value).split('.')
        if len(parts) == 2 and len(parts[1]) > 2:
            raise AccountManagementException("Invalid transfer amount")
        if value < 10 or value > 10000:
            raise AccountManagementException("Invalid transfer amount")
        return value
