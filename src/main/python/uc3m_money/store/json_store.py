"""
json_store.py

This module provides the JsonStore class, a reusable helper for
persisting Python object lists as JSON files. Handles loading,
saving, and error checking for file operations.
"""

import json
from uc3m_money.account_management_exception import AccountManagementException


class JsonStore:
    """A generic JSON store class for loading and saving item lists."""
    _data_list = []
    _FILE_NAME = ""

    def __init__(self):
        """Initializes the JsonStore and loads existing data from file."""
        self.load_list_from_file()

    def save_list_to_file(self):
        """Save the data list to the specified JSON file."""
        try:
            with open(self._FILE_NAME, "w", encoding="utf-8", newline="") as file:
                json.dump(self._data_list, file, indent=2)
        except FileNotFoundError as ex:
            raise AccountManagementException("Wrong file or file path") from ex

    def load_list_from_file(self):
        """Load the data list from the specified JSON file."""
        try:
            with open(self._FILE_NAME, "r", encoding="utf-8", newline="") as file:
                self._data_list = json.load(file)
        except FileNotFoundError:
            self._data_list = []
        except json.JSONDecodeError as ex:
            raise AccountManagementException("JSON Decode Error - Wrong JSON Format") from ex

    def add_item(self, item):
        """Add a new item (as JSON) to the list and save."""
        self.load_list_from_file()
        self._data_list.append(item.to_json())
        self.save_list_to_file()
