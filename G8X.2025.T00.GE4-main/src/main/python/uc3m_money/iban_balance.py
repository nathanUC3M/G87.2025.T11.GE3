import json
from uc3m_money import BALANCES_STORE_FILE, AccountManagementException, TRANSACTIONS_STORE_FILE
from uc3m_money.attributes.attribute_iban import AttributeIban
from datetime import  datetime, timezone


class IbanBalance():
    def __init__(self, iban):
        self._iban = AttributeIban(iban).value
        self.__last_balance_time = datetime.timestamp(datetime.now(timezone.utc))
        self.__balance = self.calculate_balance()

    def calculate_balance(self) -> bool:
        """Calculate the balance for a given iban"""
        transaction_list = self.read_transactions_file()

        iban_found = self.get_balance(transaction_list, self._iban)
        if not iban_found:
            raise AccountManagementException("IBAN not found")

        self.store_balance()
        return True

    def read_transactions_file(self):
        """Loads the content of the transactions file
        and returns a list"""
        return self._load_json_file(TRANSACTIONS_STORE_FILE)


    @staticmethod
    def get_balance(transactions: list, iban: str) -> tuple:
        """
        Calculate balance and check if IBAN exists in transactions.
        """
        balance = 0
        found = False
        for transaction in transactions:
            if transaction["IBAN"] == iban:
                balance += float(transaction["amount"])
                found = True
        return balance, found

    def store_balance(self):
        """
        Store the current balance with timestamp for the given IBAN.
        """
        entry = {
            "IBAN": self._iban,
            "time": self.__last_balance_time,
            "BALANCE": self.__balance
        }
        balance_list = self._load_json_file(BALANCES_STORE_FILE, default=[])
        balance_list.append(entry)
        self._write_json_file(BALANCES_STORE_FILE, balance_list)
