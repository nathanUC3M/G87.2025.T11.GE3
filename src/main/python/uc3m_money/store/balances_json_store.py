"""
balance_json_store.py

This module defines the BalanceJsonStore class, a specialized JSON store for
handling account balance records. Inherits from the generic JsonStore class
and uses the balances file as configured in the application.
"""

from uc3m_money.account_management_config import BALANCES_STORE_FILE
from uc3m_money.store.json_store import JsonStore


class BalanceJsonStore(JsonStore):
    """
    A JSON store class specifically for account balance records.

    Stores and retrieves balance data from the configured balances file.
    """
    _FILE_NAME = BALANCES_STORE_FILE
