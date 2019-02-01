from ibapi.contract import Contract


class Direxion(Contract):
    def __init__(self):
        Contract.__init__(self)

        self.secType = 'STK'
        self.exchange = 'SMART'
        self.currency = 'USD'
        self.primaryExchange = 'ARCA'


class DirexionBulls:

    @staticmethod
    def tawk():
        contract = Direxion()
        contract.symbol = 'TAWK'
        return contract

    @staticmethod
    def want():
        contract = Direxion()
        contract.symbol = 'WANT'
        return contract

    @staticmethod
    def need():
        contract = Direxion()
        contract.symbol = 'NEED'
        return contract

    @staticmethod
    def erx():
        contract = Direxion()
        contract.symbol = 'ERX'
        return contract

    @staticmethod
    def fas():
        contract = Direxion()
        contract.symbol = 'FAS'
        return contract

    @staticmethod
    def nugt():
        contract = Direxion()
        contract.symbol = 'NUGT'
        return contract

    @staticmethod
    def cure():
        contract = Direxion()
        contract.symbol = 'CURE'
        return contract

    @staticmethod
    def nail():
        contract = Direxion()
        contract.symbol = 'NAIL'
        return contract

    @staticmethod
    def dusl():
        contract = Direxion()
        contract.symbol = 'DUSL'
        return contract

    @staticmethod
    def jnug():
        contract = Direxion()
        contract.symbol = 'JNUG'
        return contract

    @staticmethod
    def drn():
        contract = Direxion()
        contract.symbol = 'DRN'
        return contract

    @staticmethod
    def gasl():
        contract = Direxion()
        contract.symbol = 'GASL'
        return contract

    @staticmethod
    def pill():
        contract = Direxion()
        contract.symbol = 'pill'
        return contract

    @staticmethod
    def retl():
        contract = Direxion()
        contract.symbol = 'RETL'
        return contract

    @staticmethod
    def ubot():
        contract = Direxion()
        contract.symbol = 'UBOT'
        return contract

    @staticmethod
    def labu():
        contract = Direxion()
        contract.symbol = 'LABU'
        return contract

    @staticmethod
    def gush():
        contract = Direxion()
        contract.symbol = 'GUSH'
        return contract

    @staticmethod
    def soxl():
        contract = Direxion()
        contract.symbol = 'SOXL'
        return contract

    @staticmethod
    def tecl():
        contract = Direxion()
        contract.symbol = 'TECL'
        return contract

    @staticmethod
    def tpor():
        contract = Direxion()
        contract.symbol = 'TPOR'
        return contract

    @staticmethod
    def utsl():
        contract = Direxion()
        contract.symbol = 'UTSL'
        return contract

    @staticmethod
    def dfen():
        contract = Direxion()
        contract.symbol = 'DFEN'
        return contract


class DirexionBears:
    pass