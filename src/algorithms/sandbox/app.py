import os
import logging
import datetime

from google.cloud import firestore

from ibapi import wrapper
from ibapi.client import EClient
from ibapi.contract import Contract

from common.utils.logging import setupLogger

# from common.watchlists.lev_sects import DirexionSectorBulls


TWS_PORT = int(os.getenv('TWS_PORT'))


class TestClient(EClient):
    # outgoing messages to IBKR
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)


class TestWrapper(wrapper.EWrapper):
    # incoming messages from IBKR
    def __init__(self):
        wrapper.EWrapper.__init__(self)


class TestApp(TestWrapper, TestClient):
    def __init__(self):
        TestWrapper.__init__(self)
        TestClient.__init__(self, wrapper=self)

        self.ts = datetime.datetime.now().__format__('%Y-%m-%d-%H-%M-%S')
        self.db = firestore.Client()

        self.started = False
        self.next_valid_order_id = None
        self.global_cancel = False
        self.account = None

        # data for audit app
        self.portfolio_arr = {
            "U2793185": {
                "stk": {}
            }
        }
        self.account_arr = {
            "U2793185": {
                "val": {}
            }
        }

    # #########################
    # overrides
    # #########################
    def managedAccounts(self, accountsList: str):
        super().managedAccounts(accountsList)
        self.account = accountsList.split(",")[0]

    def error(self, reqId, errorCode: int, errorString: str):
        super().error(reqId, errorCode, errorString)

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        logging.debug("setting next_valid_order_id: {o}".
                      format(o=orderId))
        self.next_valid_order_id = orderId
        self.start()

    def contractDetails(self, reqId, contractDetails):
        print('Request ID: ', reqId)
        print('Contract: ', contractDetails.contract.symbol)
        print('Long Name: ', contractDetails.longName)

    def position(self, account, contract, position, avgCost):
        if contract.secType == 'STK':
            position_obj = {
                "SecurityId": contract.secId,
                "ContractSymbol": contract.symbol,
                "PositionQty": position,
                "AvgCost": avgCost,
                "CostBasis": position * avgCost,
                "PrimaryExchange": contract.primaryExchange,
                "CurrentTimestamp": self.ts
            }
            self.portfolio_arr[contract.symbol] = position_obj
            self.db.collection(u'portfolio'). \
                document('stk'). \
                set(self.portfolio_arr)

    def updatePortfolio(self, contract: Contract, position: float,
                        marketPrice: float, marketValue: float,
                        averageCost: float, unrealizedPNL: float,
                        realizedPNL: float, accountName: str):
        super().updatePortfolio(contract, position,
                                marketPrice, marketValue,
                                averageCost, unrealizedPNL,
                                realizedPNL, accountName)

    def updateAccountValue(self, key: str, val: str, currency: str,
                           accountName: str):
        account_val_obj = {
            key: val,
            "CurrentTimestamp": self.ts
        }
        self.account_arr[self.account]['val'][key] = account_val_obj
        self.db.collection(u'account'). \
            document(key). \
            set(account_val_obj)

    # #########################
    # app utilities
    # #########################
    def nextOrderId(self):
        oid = self.next_valid_order_id
        self.next_valid_order_id += 1
        return oid

    def start(self):
        if self.started:
            return
        self.started = True

        if self.global_cancel:
            logging.info('executing global cancel')
            self.reqGlobalCancel()
        else:
            logging.info('executing requests')
            self.reqPositions()
            self.reqAccountUpdates(True, self.account)

    def stop(self):
        logging.info('stopping app')
        self.reqAccountUpdates(False, '')
        self.done = True
        self.disconnect()


def main():
    setupLogger(logging_level=logging.INFO)
    logging.info("executing job")

    app = TestApp()
    app.connect(host='127.0.0.1', port=TWS_PORT, clientId=0)

    app.run()
    app.stop()


if __name__ == '__main__':
    main()
