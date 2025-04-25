"""
Provides the IbanBalance class to calculate and serialize the balance for a given IBAN.
Handles reading transactions from a JSON file and raises AccountManagementException on errors.
"""
import json
from datetime import datetime, timezone
from src.main.python.uc3m_money.account_management_exception import AccountManagementException
from src.main.python.uc3m_money.data.attr.iban_code import IbanCode
from src.main.python.uc3m_money.account_management_config import TRANSACTIONS_STORE_FILE


class IbanBalance:
    """
    Represents the balance of an account identified by an IBAN.

    This class provides methods to calculate the balance for a specific IBAN
    by reading the transactions from a JSON file and serializing the result.
    """
    def __init__(self, iban):
        """
        Initializes the IbanBalance object, validates the IBAN,
        sets the timestamp for the balance, and calculates the balance
        """
        self._iban = IbanCode(iban).value
        self.__last_balance_time = datetime.timestamp(datetime.now(timezone.utc))
        self.__balance = self.calculate_iban_balance()

    def calculate_iban_balance(self):
        """
        Calculates the current balance for the IBAN by summing up all transactions
        associated with it.
        """

        transactions_list = self.read_transactions_file()
        iban_found = False
        current_balance = 0
        for transaction in transactions_list:
            # print(transaction["IBAN"] + " - " + iban)
            if transaction["IBAN"] == self._iban:
                current_balance += float(transaction["amount"])
                iban_found = True
        if not iban_found:
            raise AccountManagementException("IBAN not found")
        return current_balance

    @staticmethod
    def read_transactions_file():
        """loads the content of the transactions file
        and returns a list"""
        try:
            with open(TRANSACTIONS_STORE_FILE, "r", encoding="utf-8", newline="") as file:
                input_list = json.load(file)
        except FileNotFoundError as ex:
            raise AccountManagementException("Wrong file  or file path") from ex
        except json.JSONDecodeError as ex:
            raise AccountManagementException("JSON Decode Error - Wrong JSON Format") from ex
        return input_list

    def to_json(self):
        """
        Loads and parses the transactions JSON file.
        """
        return {"IBAN": self._iban,
                        "time": self.__last_balance_time,
                        "BALANCE": self.__balance}
