"""Account manager module """
import re
import json
from datetime import datetime, timezone
from uc3m_money.data.attr.iban_code import IbanCode
from src.main.python.uc3m_money.account_management_exception import AccountManagementException
from src.main.python.uc3m_money.account_management_config import (TRANSFERS_STORE_FILE,
                                        DEPOSITS_STORE_FILE,
                                        TRANSACTIONS_STORE_FILE,
                                        BALANCES_STORE_FILE)

from src.main.python.uc3m_money.transfer_request import TransferRequest
from src.main.python.uc3m_money.account_deposit import AccountDeposit


class AccountManager:
    """Class for providing the methods for managing the orders"""
    def __init__(self):
        pass

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Singleton class, allows for only one instance"""
        if cls._instance is None:
            cls._instance = super(AccountManager, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def validate_iban(modified_iban: str):
        """
    Calcula el dígito de control de un IBAN español.

    Args:
        modified_iban (str): El IBAN sin los dos últimos dígitos (dígito de control).

    Returns:
        str: El dígito de control calculado.
        """
        return IbanCode(modified_iban).value

    def validate_concept(self, concept: str):
        """regular expression for checking the minimum and maximum length as well as
        the allowed characters and spaces restrictions
        there are other ways to check this"""
        concept_format = re.compile(r"^(?=^.{10,30}$)([a-zA-Z]+(\s[a-zA-Z]+)+)$")

        valid_concept = concept_format.fullmatch(concept)
        if not valid_concept:
            raise AccountManagementException("Invalid concept format")

    def validate_transfer_date(self, transfer_date):
        """validates the arrival date format  using regex"""
        date_format = re.compile(r"^(([0-2]\d|3[0-1])\/(0\d|1[0-2])\/\d\d\d\d)$")
        valid_date = date_format.fullmatch(transfer_date)
        if not valid_date:
            raise AccountManagementException("Invalid date format")

        try:
            string_to_date = datetime.strptime(transfer_date, "%d/%m/%Y").date()
        except ValueError as ex:
            raise AccountManagementException("Invalid date format") from ex

        if string_to_date < datetime.now(timezone.utc).date():
            raise AccountManagementException("Transfer date must be today or later.")

        if string_to_date.year < 2025 or string_to_date.year > 2050:
            raise AccountManagementException("Invalid date format")
        return transfer_date

    # pylint: disable=too-many-arguments
    def transfer_request(self, from_iban: str,
                         to_iban: str,
                         concept: str,
                         transfer_type: str,
                         date: str,
                         amount: float) -> str:
        """first method: receives transfer info and
        stores it into a file"""
        self.validate_iban(from_iban)
        self.validate_iban(to_iban)
        self.validate_concept(concept)
        regex_transfer = re.compile(r"(ORDINARY|INMEDIATE|URGENT)")
        valid_transfer = regex_transfer.fullmatch(transfer_type)
        if not valid_transfer:
            raise AccountManagementException("Invalid transfer type")
        self.validate_transfer_date(date)

        try:
            float_amount = float(amount)
        except ValueError as exc:
            raise AccountManagementException("Invalid transfer amount") from exc

        float_to_string = str(float_amount)
        if '.' in float_to_string:
            decimal_places = len(float_to_string.split('.')[1])
            if decimal_places > 2:
                raise AccountManagementException("Invalid transfer amount")

        if float_amount < 10 or float_amount > 10000:
            raise AccountManagementException("Invalid transfer amount")

        transfer_request = TransferRequest(from_iban=from_iban,
                                           to_iban=to_iban,
                                           transfer_concept=concept,
                                           transfer_type=transfer_type,
                                           transfer_date=date,
                                           transfer_amount=amount)

        try:
            with open(TRANSFERS_STORE_FILE, "r", encoding="utf-8", newline="") as file:
                transfer_list = json.load(file)
        except FileNotFoundError:
            transfer_list = []
        except json.JSONDecodeError as ex:
            raise AccountManagementException("JSON Decode Error - Wrong JSON Format") from ex

        for list_index in transfer_list:
            if (list_index["from_iban"] == transfer_request.from_iban and
                    list_index["to_iban"] == transfer_request.to_iban and
                    list_index["transfer_date"] == transfer_request.transfer_date):
                if(list_index["transfer_amount"] == transfer_request.transfer_amount and
                        list_index["transfer_concept"] == transfer_request.transfer_concept and
                        list_index["transfer_type"] == transfer_request.transfer_type):
                        raise AccountManagementException("Duplicated transfer in transfer list")

        transfer_list.append(transfer_request.to_json())

        try:
            with open(TRANSFERS_STORE_FILE, "w", encoding="utf-8", newline="") as file:
                json.dump(transfer_list, file, indent=2)
        except FileNotFoundError as ex:
            raise AccountManagementException("Wrong file  or file path") from ex
        except json.JSONDecodeError as ex:
            raise AccountManagementException("JSON Decode Error - Wrong JSON Format") from ex

        return transfer_request.transfer_code

    def deposit_into_account(self, input_file: str) -> str:
        """manages the deposits received for accounts"""
        try:
            with open(input_file, "r", encoding="utf-8", newline="") as file:
                input_dictionary = json.load(file)
        except FileNotFoundError as ex:
            raise AccountManagementException("Error: file input not found") from ex
        except json.JSONDecodeError as ex:
            raise AccountManagementException("JSON Decode Error - Wrong JSON Format") from ex

        # comprobar valores del fichero
        try:
            deposit_iban = input_dictionary["IBAN"]
            deposit_amount = input_dictionary["AMOUNT"]
        except KeyError as e:
            raise AccountManagementException("Error - Invalid Key in JSON") from e

        deposit_iban = self.validate_iban(deposit_iban)
        amount_format = re.compile(r"^EUR [0-9]{4}\.[0-9]{2}")
        valid_amount = amount_format.fullmatch(deposit_amount)
        if not valid_amount:
            raise AccountManagementException("Error - Invalid deposit amount")

        value_amount = float(deposit_amount[4:])
        if value_amount == 0:
            raise AccountManagementException("Error - Deposit must be greater than 0")

        deposit_obj = AccountDeposit(to_iban=deposit_iban,
                                     deposit_amount=value_amount)

        try:
            with open(DEPOSITS_STORE_FILE, "r", encoding="utf-8", newline="") as file:
                deposit_list = json.load(file)
        except FileNotFoundError as ex:
            deposit_list = []
        except json.JSONDecodeError as ex:
            raise AccountManagementException("JSON Decode Error - Wrong JSON Format") from ex

        deposit_list.append(deposit_obj.to_json())

        try:
            with open(DEPOSITS_STORE_FILE, "w", encoding="utf-8", newline="") as file:
                json.dump(deposit_list, file, indent=2)
        except FileNotFoundError as ex:
            raise AccountManagementException("Wrong file  or file path") from ex
        except json.JSONDecodeError as ex:
            raise AccountManagementException("JSON Decode Error - Wrong JSON Format") from ex

        return deposit_obj.deposit_signature


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


    def calculate_balance(self, iban:str)->bool:
        """calculate the balance for a given iban"""
        iban = self.validate_iban(iban)
        t_l = self.read_transactions_file()
        iban_found = False
        bal_s = 0
        for transaction in t_l:
            #print(transaction["IBAN"] + " - " + iban)
            if transaction["IBAN"] == iban:
                bal_s += float(transaction["amount"])
                iban_found = True
        if not iban_found:
            raise AccountManagementException("IBAN not found")

        last_balance = {"IBAN": iban,
                        "time": datetime.timestamp(datetime.now(timezone.utc)),
                        "BALANCE": bal_s}

        try:
            with open(BALANCES_STORE_FILE, "r", encoding="utf-8", newline="") as file:
                balance_list = json.load(file)
        except FileNotFoundError:
            balance_list = []
        except json.JSONDecodeError as ex:
            raise AccountManagementException("JSON Decode Error - Wrong JSON Format") from ex

        balance_list.append(last_balance)

        try:
            with open(BALANCES_STORE_FILE, "w", encoding="utf-8", newline="") as file:
                json.dump(balance_list, file, indent=2)
        except FileNotFoundError as ex:
            raise AccountManagementException("Wrong file  or file path") from ex
        return True
