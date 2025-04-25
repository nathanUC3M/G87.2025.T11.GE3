from uc3m_money import AccountManagementException
from uc3m_money.account_management_config import DEPOSITS_STORE_FILE
from uc3m_money.store.json_store import JsonStore


class DepositJsonStore(JsonStore):
    _FILE_NAME = DEPOSITS_STORE_FILE

