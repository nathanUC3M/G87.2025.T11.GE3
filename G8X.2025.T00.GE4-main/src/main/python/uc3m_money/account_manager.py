"""Account manager module """
import re
import json
from datetime import datetime, timezone
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

    @staticmethod
    def validate_iban(modified_iban: str):
        """
    Calcula el dígito de control de un IBAN español.

    Args:
        modified_iban (str): El IBAN sin los dos últimos dígitos (dígito de control).

    Returns:
        str: El dígito de control calculado.
        """
        country_code_check = re.compile(r"^ES[0-9]{22}")
        valid_iban = country_code_check.fullmatch(modified_iban)
        if not valid_iban:
            raise AccountManagementException("Invalid IBAN format")
        iban = modified_iban
        original_code = iban[2:4]
        #replacing the control
        iban = iban[:2] + "00" + iban[4:]
        iban = iban[4:] + iban[:4]


        # Convertir el IBAN en una cadena numérica, reemplazando letras por números
        iban = (iban.replace('A', '10').replace('B', '11').
                replace('C', '12').replace('D', '13').replace('E', '14').
                replace('F', '15'))
        iban = (iban.replace('G', '16').replace('H', '17').
                replace('I', '18').replace('J', '19').replace('K', '20').
                replace('L', '21'))
        iban = (iban.replace('M', '22').replace('N', '23').
                replace('O', '24').replace('P', '25').replace('Q', '26').
                replace('R', '27'))
        iban = (iban.replace('S', '28').replace('T', '29').replace('U', '30').
                replace('V', '31').replace('W', '32').replace('X', '33'))
        iban = iban.replace('Y', '34').replace('Z', '35')

        # Mover los cuatro primeros caracteres al final

        # Convertir la cadena en un número entero
        iban_integer = int(iban)

        # Calcular el módulo 97
        iban_mod = iban_integer % 97

        # Calcular el dígito de control (97 menos el módulo)
        valid_check_digits = 98 - iban_mod

        if int(original_code) != valid_check_digits:
            #print(valid_check_digits)
            raise AccountManagementException("Invalid IBAN control digit")

        return modified_iban

    def validate_concept(self, concept: str):
        """Regular expression for checking the minimum and maximum length as well as
        the allowed characters and spaces restrictions
        there are other ways to check this"""
        concept_format = re.compile(r"^(?=^.{10,30}$)([a-zA-Z]+(\s[a-zA-Z]+)+)$")

        valid_concept = concept_format.fullmatch(concept)
        if not valid_concept:
            raise AccountManagementException ("Invalid concept format")

    def validate_transfer_date(self, transfer_date):
        """Validates the arrival date format  using regex"""
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
    #pylint: disable=too-many-arguments
    def validate_transfer_details(self, from_iban: str,
                         to_iban: str,
                         concept: str,
                         transfer_type: str,
                         date: str,
                         amount: float)->str:
        """
        Makes sure the transfer details are finalized,
        including the from and to iban, the concept, and
        the transfer
        """
        self.validate_iban(from_iban)
        self.validate_iban(to_iban)
        self.validate_concept(concept)
        regex_transfer = re.compile(r"(ORDINARY|INMEDIATE|URGENT)")
        valid_transfer = regex_transfer.fullmatch(transfer_type)
        if not valid_transfer:
            raise AccountManagementException("Invalid transfer type")
        self.validate_transfer_date(date)
        self.validate_transfer_amount(amount)

    @staticmethod
    def validate_transfer_amount(amount: float):
        """
        Validate the transfer amount ensuring it is a float with up to two decimal places
        and within the allowed range (10 to 10,000).
        """
        try:
            float_amount  = float(amount)
        except ValueError as exc:
            raise AccountManagementException("Invalid transfer amount") from exc

        float_to_string = str(float_amount)
        if '.' in float_to_string:
            decimal_places = len(float_to_string.split('.')[1])
            if decimal_places > 2:
                raise AccountManagementException("Invalid transfer amount")

        if float_amount < 10 or float_amount > 10000:
            raise AccountManagementException("Invalid transfer amount")

    @staticmethod
    def check_duplicate(incoming_transfer: dict, transfer_list: list) -> bool:
        """
        Check if a transfer already exists in the transfer list with matching fields.
        Returns True if a duplicate is found, otherwise False.
        """
        for existing in transfer_list:
            if (existing["from_iban"] == incoming_transfer["from_iban"] and
                existing["to_iban"] == incoming_transfer["to_iban"] and
                existing["transfer_date"] == incoming_transfer["transfer_date"]):
                if (existing["transfer_amount"] == incoming_transfer["transfer_amount"] and
                    existing["transfer_concept"] == incoming_transfer["transfer_concept"] and
                    existing["transfer_type"] == incoming_transfer["transfer_type"]):
                    return True
        return False

    @staticmethod
    def _load_transfer_list() -> list:
        """
        Load the list of transfers from the transfer store file.
        Returns an empty list if the file does not exist.
        """
        try:
            with open(TRANSFERS_STORE_FILE, "r", encoding="utf-8", newline="") as file:
                return json.load(file)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError as ex:
            raise AccountManagementException("JSON Decode Error - Wrong JSON Format") from ex

    @staticmethod
    def _save_transfer_list(transfer_list: list):
        """
        Save the list of transfers to the transfer store file.
        """
        with open(TRANSFERS_STORE_FILE, "w", encoding="utf-8", newline="") as file:
            json.dump(transfer_list, file, indent=2)

    # pylint: disable=too-many-arguments
    def transfer_request(self, from_iban: str, to_iban: str, concept: str,
                     transfer_type: str, date: str, amount: float) -> str:
        """
         Process a new transfer request and store it if it's valid and not a duplicate.
         Returns the generated transfer code.
         """
        self.validate_transfer_details(from_iban, to_iban, concept, transfer_type, date, amount)

        transfer_request = TransferRequest(from_iban=from_iban,
                                     to_iban=to_iban,
                                     transfer_concept=concept,
                                     transfer_type=transfer_type,
                                     transfer_date=date,
                                     transfer_amount=amount)

        transfer_json = transfer_request.to_json()
        transfer_list = self._load_transfer_list()


        if self.check_duplicate(transfer_json, transfer_list):
            raise AccountManagementException("Duplicated transfer in transfer list")

        transfer_list.append(transfer_json)
        self._save_transfer_list(transfer_list)

        return transfer_request.transfer_code

    def validate_deposit_iban(self, input_data: dict) -> str:
        """
        Validate the IBAN from the deposit input data.
        """
        try:
            return self.validate_iban(input_data["IBAN"])
        except KeyError as e:
            raise AccountManagementException("Error - Invalid Key in JSON") from e

    @staticmethod
    def validate_deposit_amount(input_data: dict) -> float:
        """
        Validate and convert the deposit amount from the input data.
        """
        try:
            deposit_amount = input_data["AMOUNT"]
        except KeyError as e:
            raise AccountManagementException("Error - Invalid Key in JSON") from e

        amount_format = re.compile(r"^EUR [0-9]{4}\.[0-9]{2}")
        if not amount_format.fullmatch(deposit_amount):
            raise AccountManagementException("Error - Invalid deposit amount")

        value_amount = float(deposit_amount[4:])
        if value_amount == 0:
            raise AccountManagementException("Error - Deposit must be greater than 0")

        return value_amount

    @staticmethod
    def _load_json_file(filepath: str, default=None):
        """
        Load JSON data from a file or return default if file is missing.
        """
        try:
            with open(filepath, "r", encoding="utf-8", newline="") as file:
                return json.load(file)
        except FileNotFoundError as exc:
            if default is not None:
                return default
            raise AccountManagementException("Wrong file  or file path") from exc
        except json.JSONDecodeError as exc:
            raise AccountManagementException("JSON Decode Error - Wrong JSON Format") from exc

    @staticmethod
    def _write_json_file(filepath: str, data: list):
        """
        Writes a list of data to a JSON file at the specified filepath.
        """
        try:
            with open(filepath, "w", encoding="utf-8", newline="") as file:
                json.dump(data, file, indent=2)
        except FileNotFoundError as exc:
            raise AccountManagementException("Wrong file  or file path") from exc
        except json.JSONDecodeError as exc:
            raise AccountManagementException("JSON Decode Error - Wrong JSON Format") from exc

    def deposit_into_account(self, input_file:str)->str:
        """Manages the deposits received for accounts"""
        input_data = self._load_json_file(input_file)

        deposit_iban = self.validate_deposit_iban(input_data)
        value_amount = self.validate_deposit_amount(input_data)

        deposit_obj = AccountDeposit(to_iban=deposit_iban, deposit_amount=value_amount)

        deposit_list = self._load_json_file(DEPOSITS_STORE_FILE, default=[])
        deposit_list.append(deposit_obj.to_json())
        self._write_json_file(DEPOSITS_STORE_FILE, deposit_list)

        return deposit_obj.deposit_signature

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

    def store_balance(self, iban: str, balance: float):
        """
        Store the current balance with timestamp for the given IBAN.
        """
        entry = {
            "IBAN": iban,
            "time": datetime.timestamp(datetime.now(timezone.utc)),
            "BALANCE": balance
        }
        balance_list = self._load_json_file(BALANCES_STORE_FILE, default=[])
        balance_list.append(entry)
        self._write_json_file(BALANCES_STORE_FILE, balance_list)

    def calculate_balance(self, iban: str) -> bool:
        """Calculate the balance for a given iban"""
        iban = self.validate_iban(iban)
        transaction_list = self.read_transactions_file()

        balance_count, iban_found = self.get_balance(transaction_list, iban)
        if not iban_found:
            raise AccountManagementException("IBAN not found")

        self.store_balance(iban, balance_count)
        return True
