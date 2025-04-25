from uc3m_money.account_management_exception import AccountManagementException
from uc3m_money.data.attr.iban_code import IbanCode
from uc3m_money.account_management_config import TRANSACTIONS_STORE_FILE
from datetime import datetime, timezone
import json

class IbanBalance():
    def __init__(self, iban):
        self.iban = IbanCode(iban).value
        self.__last_balance_time = datetime.timestamp(datetime.now(timezone.utc))
        self.__balance = self.calculate_iban_balance()

    def calculate_iban_balance(self):
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

    def read_transactions_file(self):
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
        return {"IBAN": self.iban,
                        "time": self.__last_balance_time,
                        "BALANCE": self.__balance}