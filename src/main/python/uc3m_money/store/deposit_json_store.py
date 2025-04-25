"""
deposit_json_store.py

This module defines the DepositJsonStore class for managing deposit
records in a persistent JSON file. Inherits from the generic
JsonStore helper and configures it to use the deposits file
specified in the application configuration.
"""

from uc3m_money import AccountManagementException
from uc3m_money.account_management_config import DEPOSITS_STORE_FILE
from uc3m_money.store.json_store import JsonStore


class DepositJsonStore(JsonStore):
    """A JSON store class specifically for deposit records."""
    _FILE_NAME = DEPOSITS_STORE_FILE
