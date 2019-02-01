from ibapi.contract import Contract


class Direxion(Contract):
    def __init__(self):
        Contract.__init__(self)

        self.secType = 'STK'
        self.exchange = 'SMART'
        self.currency = 'USD'
        self.primaryExchange = 'ARCA'


class DirexionIntlEqBulls:

    @staticmethod
    def euxl():
        contract = Direxion()
        contract.symbol = 'EUXL'
        return contract

    @staticmethod
    def yinn():
        contract = Direxion()
        contract.symbol = 'YINN'
        return contract

    @staticmethod
    def eurl():
        contract = Direxion()
        contract.symbol = 'EURL'
        return contract

    @staticmethod
    def lbj():
        contract = Direxion()
        contract.symbol = 'LBJ'
        return contract

    @staticmethod
    def brzu():
        contract = Direxion()
        contract.symbol = 'BRZU'
        return contract

    @staticmethod
    def dzk():
        contract = Direxion()
        contract.symbol = 'DZK'
        return contract

    @staticmethod
    def edc():
        contract = Direxion()
        contract.symbol = 'EDC'
        return contract

    @staticmethod
    def indl():
        contract = Direxion()
        contract.symbol = 'INDL'
        return contract

    @staticmethod
    def jpnl():
        contract = Direxion()
        contract.symbol = 'JPNL'
        return contract

    @staticmethod
    def mexx():
        contract = Direxion()
        contract.symbol = 'MEXX'
        return contract

    @staticmethod
    def koru():
        contract = Direxion()
        contract.symbol = 'KORU'
        return contract

    @staticmethod
    def rusl():
        contract = Direxion()
        contract.symbol = 'RUSL'
        return contract


class DirexionIntlEqBears:

    @staticmethod
    def yang():
        contract = Direxion()
        contract.symbol = 'YANG'
        return contract

    @staticmethod
    def dpk():
        contract = Direxion()
        contract.symbol = 'DPK'
        return contract

    @staticmethod
    def edz():
        contract = Direxion()
        contract.symbol = 'EDZ'
        return contract

    @staticmethod
    def russ():
        contract = Direxion()
        contract.symbol = 'RUSS'
        return contract
