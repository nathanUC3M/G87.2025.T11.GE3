"""
transfers_json_store.py

This module defines the TransfersJsonStore class, a specialized JSON store for
handling transfer records. It ensures duplicate transfers are not added to the
store. Inherits from the generic JsonStore class and uses the transfers file
as configured in the application.
"""

from src.main.python.uc3m_money import AccountManagementException
from src.main.python.uc3m_money.account_management_config import TRANSFERS_STORE_FILE
from src.main.python.uc3m_money.store.json_store import JsonStore


class TransfersJsonStore(JsonStore):
    """
    A JSON store class specifically for transfer records.

    Prevents adding duplicate transfers to the store.
    """

    _data_list = []
    _FILE_NAME = TRANSFERS_STORE_FILE

    def add_item(self, item):
        """
        Add a new transfer to the store, checking for duplicates first.
        """
        self.load_list_from_file()
        for old_transfer in self._data_list:  # Prevent duplicates
            if old_transfer == item.to_json():
                raise AccountManagementException("Duplicated transfer in transfer list")
        super().add_item(item)
