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
    def _load_json_file(filepath, empty_value):
        """
        Helper to load JSON from file, returning `empty_value` if the file is not found.
        Raises AccountManagementException if the JSON format is invalid.
        """
        try:
            with open(filepath, "r", encoding="utf-8", newline="") as file:
                return json.load(file)
        except FileNotFoundError:
            return empty_value
        except json.JSONDecodeError as ex:
            raise AccountManagementException("JSON Decode Error - Wrong JSON Format") from ex

    @staticmethod
    def _save_json_file(filepath, data):
        """
        Helper to save JSON data to file, with error handling.
        Raises AccountManagementException for file or JSON errors.
        """
        try:
            with open(filepath, "w", encoding="utf-8", newline="") as file:
                json.dump(data, file, indent=2)
        except FileNotFoundError as ex:
            raise AccountManagementException("Wrong file or file path") from ex
        except json.JSONDecodeError as ex:
            raise AccountManagementException("JSON Decode Error - Wrong JSON Format") from ex

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

        # Move the first four characters to the end

        # Convert to integer
        iban_integer = int(iban)

        # Calculate the modulus check
        iban_mod = iban_integer % 97

        # Calculate the control digit
        valid_check_digits = 98 - iban_mod

        if int(original_code) != valid_check_digits:
            #print(valid_check_digits)
            raise AccountManagementException("Invalid IBAN control digit")

        return modified_iban

    def validate_concept(self, concept: str):
        """regular expression for checking the minimum and maximum length as well as
        the allowed characters and spaces restrictions
        there are other ways to check this"""
        concept_format = re.compile(r"^(?=^.{10,30}$)([a-zA-Z]+(\s[a-zA-Z]+)+)$")

        valid_concept = concept_format.fullmatch(concept)
        if not valid_concept:
            raise AccountManagementException ("Invalid concept format")

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
    #pylint: disable=too-many-arguments
    def transfer_request(self, from_iban: str,
                         to_iban: str,
                         concept: str,
                         transfer_type: str,
                         date: str,
                         amount: float)->str:
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

        transfer_request = TransferRequest(from_iban=from_iban,
                                     to_iban=to_iban,
                                     transfer_concept=concept,
                                     transfer_type=transfer_type,
                                     transfer_date=date,
                                     transfer_amount=amount)

        transfer_list = self._load_json_file(TRANSFERS_STORE_FILE, [])

        for list_index in transfer_list:
            if (list_index["from_iban"] == transfer_request.from_iban and
                    list_index["to_iban"] == transfer_request.to_iban and
                    list_index["transfer_date"] == transfer_request.transfer_date and
                    list_index["transfer_amount"] == transfer_request.transfer_amount and
                    list_index["transfer_concept"] == transfer_request.transfer_concept and
                    list_index["transfer_type"] == transfer_request.transfer_type):
                raise AccountManagementException("Duplicated transfer in transfer list")

        transfer_list.append(transfer_request.to_json())

        self._save_json_file(TRANSFERS_STORE_FILE, transfer_list)
        return transfer_request.transfer_code

    def deposit_into_account(self, input_file:str)->str:
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

        deposit_list = self._load_json_file(DEPOSITS_STORE_FILE, [])
        deposit_list.append(deposit_obj.to_json())

        self._save_json_file(DEPOSITS_STORE_FILE, deposit_list)
        return deposit_obj.deposit_signature


    def read_transactions_file(self):
        """loads the content of the transactions file
        and returns a list"""
        return self._load_json_file(TRANSACTIONS_STORE_FILE, [])


    def calculate_balance(self, iban:str)->bool:
        """calculate the balance for a given iban"""
        iban = self.validate_iban(iban)
        transaction_list = self.read_transactions_file()
        iban_found = False
        balance_count = 0
        for transaction in transaction_list:
            #print(transaction["IBAN"] + " - " + iban)
            if transaction["IBAN"] == iban:
                balance_count += float(transaction["amount"])
                iban_found = True
        if not iban_found:
            raise AccountManagementException("IBAN not found")

        last_balance = {"IBAN": iban,
                        "time": datetime.timestamp(datetime.now(timezone.utc)),
                        "BALANCE": balance_count}

        balance_list = self._load_json_file(BALANCES_STORE_FILE, [])
        balance_list.append(last_balance)

        self._save_json_file(BALANCES_STORE_FILE, balance_list)
        return True
