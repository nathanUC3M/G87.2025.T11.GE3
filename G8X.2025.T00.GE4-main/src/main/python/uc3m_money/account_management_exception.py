"""Exception for the order_management module"""

class AccountManagementException(Exception):
    """Personalised exception for Accounts Management"""
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    @property
    def message(self):
        """gets the message value"""
        return self.__message

    @message.setter
    def message(self,value):
        """Sets the message value"""
        self.__message = value
