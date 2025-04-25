from uc3m_money import AccountManagementException
from uc3m_money.account_management_config import TRANSFERS_STORE_FILE
from uc3m_money.store.json_store import JsonStore


class TransfersJsonStore(JsonStore):
    _data_list = []
    _FILE_NAME = TRANSFERS_STORE_FILE

    def add_item(self, item):
        """Overrides the original method including the logic"""
        self.load_list_from_file()
        for old_transfer in self._data_list:  # look up a previous transfer in order not to duplicate
            if old_transfer == item.to_json():
                raise AccountManagementException("Duplicated transfer in transfer list")
        super().add_item(item)