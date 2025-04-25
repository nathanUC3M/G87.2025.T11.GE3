from uc3m_money.account_management_exception import AccountManagementException
from uc3m_money.account_management_config import BALANCES_STORE_FILE
from uc3m_money.store.json_store import JsonStore


class BalanceJsonStore(JsonStore):
    _FILE_NAME = BALANCES_STORE_FILE