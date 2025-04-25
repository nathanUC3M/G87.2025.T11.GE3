import re
from uc3m_money.account_management_exception import AccountManagementException

class TransferTypeValidator:
    @staticmethod
    def validate(transfer_type: str) -> None:
        """
        Validates the transfer type:
        Must be one of ORDINARY, INMEDIATE, URGENT
        """
        if not re.fullmatch(r"^(ORDINARY|INMEDIATE|URGENT)$", transfer_type):
            raise AccountManagementException("Invalid transfer type")