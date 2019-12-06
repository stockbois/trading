from ibapi.contract import Contract


class Direxion(Contract):
    def __init__(self):
        Contract.__init__(self)

        self.secType = 'STK'
        self.exchange = 'SMART'
        self.currency = 'USD'
        self.primaryExchange = 'ARCA'


class DirexionFixIncBulls:

    @staticmethod
    def tmf():
        contract = Direxion()
        contract.symbol = 'TMF'
        return contract

    @staticmethod
    def tyd():
        contract = Direxion()
        contract.symbol = 'TYD'
        return contract


class DirexionFixIncBears:

    @staticmethod
    def tmv():
        contract = Direxion()
        contract.symbol = 'TMV'
        return contract

    @staticmethod
    def tyo():
        contract = Direxion()
        contract.symbol = 'TYO'
        return contract


def Test():
    from ibapi.utils import ExerciseStaticMethods
    ExerciseStaticMethods(Direxion)
    ExerciseStaticMethods(DirexionFixIncBulls)
    ExerciseStaticMethods(DirexionFixIncBears)


if "__main__" == __name__:
    Test()
