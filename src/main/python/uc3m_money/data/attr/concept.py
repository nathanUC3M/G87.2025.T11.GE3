import re
from uc3m_money.account_management_exception import AccountManagementException

class ConceptValidator:
    @staticmethod
    def validate(concept: str) -> None:
        """
        Validates the transfer concept:
        - Length between 10 and 30 characters
        - Only letters and spaces
        - At least two words
        """
        pattern = re.compile(r"^(?=.{10,30}$)([A-Za-z]+(\s[A-Za-z]+)+)$")
        if not pattern.fullmatch(concept):
            raise AccountManagementException("Invalid concept format")