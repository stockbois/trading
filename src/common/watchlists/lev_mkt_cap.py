from ibapi.contract import Contract


class Direxion(Contract):
    def __init__(self):
        Contract.__init__(self)

        self.secType = 'STK'
        self.exchange = 'SMART'
        self.currency = 'USD'
        self.primaryExchange = 'ARCA'


class DirexionMktCapBulls:

    @staticmethod
    def midu():
        contract = Direxion()
        contract.symbol = 'MIDU'
        return contract

    @staticmethod
    def spxl():
        contract = Direxion()
        contract.symbol = 'SPXL'
        return contract

    @staticmethod
    def tna():
        contract = Direxion()
        contract.symbol = 'TNA'
        return contract


class DirexionMktCapBears:

    @staticmethod
    def midz():
        contract = Direxion()
        contract.symbol = 'MIDZ'
        return contract

    @staticmethod
    def spxs():
        contract = Direxion()
        contract.symbol = 'SPXS'
        return contract

    @staticmethod
    def tza():
        contract = Direxion()
        contract.symbol = 'TZA'
        return contract


def Test():
    from ibapi.utils import ExerciseStaticMethods
    ExerciseStaticMethods(Direxion)
    ExerciseStaticMethods(DirexionMktCapBulls)
    ExerciseStaticMethods(DirexionMktCapBears)


if "__main__" == __name__:
    Test()
