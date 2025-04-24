"""Contains the class AccountDeposit"""
from datetime import datetime, timezone
import hashlib


class AccountDeposit:
    """Class representing the information required for a deposit"""

    def __init__(self, to_iban: str, deposit_amount: float):
        self.__alg = "SHA-256"
        self.__type = "DEPOSIT"
        self.__to_iban = to_iban
        self.__deposit_amount = deposit_amount
        current_time = datetime.now(timezone.utc)
        self.__deposit_date = datetime.timestamp(current_time)

    def to_json(self):
        """Returns the object data in json format"""
        return {
            "alg": self.__alg,
            "type": self.__type,
            "to_iban": self.__to_iban,
            "deposit_amount": self.__deposit_amount,
            "deposit_date": self.__deposit_date,
            "deposit_signature": self.deposit_signature
        }

    def __signature_string(self):
        """Composes the string to be used for generating the key for the date"""
        return (
            "{alg:" + str(self.__alg) +
            ",typ:" + str(self.__type) +
            ",iban:" + str(self.__to_iban) +
            ",amount:" + str(self.__deposit_amount) +
            ",deposit_date:" + str(self.__deposit_date) + "}"
        )

    @property
    def to_iban(self):
        """Property that represents the IBAN"""
        return self.__to_iban

    @to_iban.setter
    def to_iban(self, value):
        self.__to_iban = value

    @property
    def deposit_amount(self):
        """Property that represents the deposit amount"""
        return self.__deposit_amount

    @deposit_amount.setter
    def deposit_amount(self, value):
        self.__deposit_amount = value

    @property
    def deposit_date(self):
        """Property that represents the deposit date"""
        return self.__deposit_date

    @deposit_date.setter
    def deposit_date(self, value):
        self.__deposit_date = value

    @property
    def deposit_signature(self):
        """Returns the SHA-256 signature of the data"""
        return hashlib.sha256(self.__signature_string().encode()).hexdigest()
