import os

from ibapi import wrapper
from ibapi.client import EClient
from ibapi.contract import Contract


TWS_PORT=int(os.getenv('TWS_PORT'))


class TestClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)


class TestWrapper(wrapper.EWrapper):
    def __init__(self):
        wrapper.EWrapper.__init__(self)


class TestApp(TestWrapper, TestClient):
    def __init__(self):
        TestClient.__init__(self, self)

    def error(self, reqId, errorCode:int, errorString:str):
        print("Error: ", reqId, " ", errorCode, " ", errorString)

    def contractDetails(self, reqId, contractDetails):
        print("Contract Details: ", reqId, " ", contractDetails)


class Watchlist():
    @staticmethod
    def aapl():
        contract = Contract()
        contract.symbol = 'AAPL'
        contract.secType = 'STK'
        contract.exchange = 'SMART'
        contract.currency = 'USD'
        contract.primaryExchange = 'NASDAQ'
        return contract


def main():
    app = TestApp()

    app.connect(host='127.0.0.1', port=TWS_PORT, clientId=0)

    app.reqContractDetails(1, Watchlist.aapl())

    app.run()


if __name__ == '__main__':
    main()