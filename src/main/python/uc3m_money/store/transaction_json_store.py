from uc3m_money import AccountManagementException
from uc3m_money.account_management_config import TRANSACTIONS_STORE_FILE
from uc3m_money.store.json_store import JsonStore


class TransactionJsonStore(JsonStore):
    _FILE_NAME = TRANSACTIONS_STORE_FILE

    def find_all(self, key, value):
        """returns a list with the items that contains the pair key:value received . The business logic concerning the sum o take away is in other class """
        self.load_list_from_file()
        result_list = []
        for item in self._data_list:
            if item[key] == value:
                result_list.append(item)
        return result_list

