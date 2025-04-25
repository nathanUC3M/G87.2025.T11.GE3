"""Account manager module """
import re
import json
from uc3m_money.account_management_exception import AccountManagementException
from uc3m_money.account_management_config import (BALANCES_STORE_FILE)
from uc3m_money.iban_balance import IbanBalance
from uc3m_money.store.transfers_json_store import TransfersJsonStore
from uc3m_money.transfer_request import TransferRequest
from uc3m_money.account_deposit import AccountDeposit
from uc3m_money.store.deposit_json_store import DepositJsonStore


class AccountManager:
    """Class for providing the methods for managing the orders"""
    def __init__(self):
        pass

    def transfer_request(self, from_iban: str,
                         to_iban: str,
                         concept: str,
                         transfer_type: str,
                         date: str,
                         amount: float)->str:
        """first method: receives transfer info and
        stores it into a file"""

        self.validate_concept(concept)
        mr = re.compile(r"(ORDINARY|INMEDIATE|URGENT)")
        res = mr.fullmatch(transfer_type)
        if not res:
            raise AccountManagementException("Invalid transfer type")
        self.validate_transfer_date(date)



        try:
            f_amount  = float(amount)
        except ValueError as exc:
            raise AccountManagementException("Invalid transfer amount") from exc

        n_str = str(f_amount)
        if '.' in n_str:
            decimales = len(n_str.split('.')[1])
            if decimales > 2:
                raise AccountManagementException("Invalid transfer amount")

        if f_amount < 10 or f_amount > 10000:
            raise AccountManagementException("Invalid transfer amount")

        my_request = TransferRequest(from_iban=from_iban,
                                     to_iban=to_iban,
                                     transfer_concept=concept,
                                     transfer_type=transfer_type,
                                     transfer_date=date,
                                     transfer_amount=amount)

        transfers_store = TransfersJsonStore()
        transfers_store.add_item(my_request)

        return my_request.transfer_code

    def deposit_into_account(self, input_file:str)->str:
        """manages the deposits received for accounts"""
        try:
            with open(input_file, "r", encoding="utf-8", newline="") as file:
                i_d = json.load(file)
        except FileNotFoundError as ex:
            raise AccountManagementException("Error: file input not found") from ex
        except json.JSONDecodeError as ex:
            raise AccountManagementException("JSON Decode Error - Wrong JSON Format") from ex

        # comprobar valores del fichero
        try:
            deposit_iban = i_d["IBAN"]
            deposit_amount = i_d["AMOUNT"]
        except KeyError as e:
            raise AccountManagementException("Error - Invalid Key in JSON") from e


        deposit_iban = self.valivan(deposit_iban)
        myregex = re.compile(r"^EUR [0-9]{4}\.[0-9]{2}")
        res = myregex.fullmatch(deposit_amount)
        if not res:
            raise AccountManagementException("Error - Invalid deposit amount")

        d_a_f = float(deposit_amount[4:])
        if d_a_f == 0:
            raise AccountManagementException("Error - Deposit must be greater than 0")

        deposit_obj = AccountDeposit(to_iban=deposit_iban,
                                     deposit_amount=deposit_amount)

        deposits_json_store = DepositJsonStore()
        deposits_json_store.add_item(deposit_obj)
        return deposit_obj.deposit_signature



    def calculate_balance(self, iban:str)->bool:
        """calculate the balance for a given iban"""

        iban_balance = IbanBalance(iban)
        try:
            with open(BALANCES_STORE_FILE, "r", encoding="utf-8", newline="") as file:
                balance_list = json.load(file)
        except FileNotFoundError:
            balance_list = []
        except json.JSONDecodeError as ex:
            raise AccountManagementException("JSON Decode Error - Wrong JSON Format") from ex

        balance_list.append(iban_balance.to_json())

        try:
            with open(BALANCES_STORE_FILE, "w", encoding="utf-8", newline="") as file:
                json.dump(balance_list, file, indent=2)
        except FileNotFoundError as ex:
            raise AccountManagementException("Wrong file  or file path") from ex
        return True

