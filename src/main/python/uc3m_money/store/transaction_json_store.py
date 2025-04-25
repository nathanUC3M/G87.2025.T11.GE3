"""
transaction_json_store.py

This module provides the TransactionJsonStore class, which is a specialized
JSON store for managing transaction records. Inherits from the generic
JsonStore class and configures it to use the transactions file defined
in the application configuration.

Includes a helper method for retrieving all items matching a specific key-value pair.
"""

from src.main.python.uc3m_money.account_management_config import TRANSACTIONS_STORE_FILE
from src.main.python.uc3m_money.store.json_store import JsonStore


class TransactionJsonStore(JsonStore):
    """A JSON store class specifically for transaction records."""

    _FILE_NAME = TRANSACTIONS_STORE_FILE

    def find_all(self, key, value):
        """
        Return a list of items where the given key matches the given value.

        Args:
            key (str): The key to search for.
            value (Any): The value to match against.

        Returns:
            list: A list of matching items (dictionaries).
        """
        self.load_list_from_file()
        result_list = []
        for item in self._data_list:
            if item[key] == value:
                result_list.append(item)
        return result_list
