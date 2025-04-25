import re
from datetime import datetime, timezone
from uc3m_money.account_management_exception import AccountManagementException

class TransferDateValidator:
    @staticmethod
    def validate(date_str: str) -> str:
        """
        Validates the transfer date:
        - Format DD/MM/YYYY
        - No earlier than today
        - Year between 2025 and 2050 inclusive
        """
        pattern = re.compile(r"^([0-3]\d)/(0[1-9]|1[0-2])/([0-9]{4})$")
        if not pattern.fullmatch(date_str):
            raise AccountManagementException("Invalid date format")
        try:
            parsed = datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError as ex:
            raise AccountManagementException("Invalid date format") from ex
        if parsed < datetime.now(timezone.utc).date():
            raise AccountManagementException("Transfer date must be today or later.")
        if parsed.year < 2025 or parsed.year > 2050:
            raise AccountManagementException("Invalid date format")
        return date_str
