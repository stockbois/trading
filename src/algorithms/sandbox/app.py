import os
import logging

from ibapi import wrapper
from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.utils import iswrapper

from common.watchlists.lev_sects import DirexionSectorBulls
from common.utils.logging import setupLogger

from ibapi.account_summary_tags import AccountSummaryTags

# from ibapi.common import *  # @UnusedWildImport
# from ibapi.order_condition import *  # @UnusedWildImport
# from ibapi.contract import *  # @UnusedWildImport
# from ibapi.order import *  # @UnusedWildImport
# from ibapi.order_state import *  # @UnusedWildImport
# from ibapi.execution import Execution
# from ibapi.execution import ExecutionFilter
# from ibapi.commission_report import CommissionReport
# from ibapi.ticktype import *  # @UnusedWildImport
# from ibapi.tag_value import TagValue

TWS_PORT = int(os.getenv('TWS_PORT'))


def printWhenExecuting(fn):
    def fn2(self):
        logging.info('executing {fn}', fn=fn.__name__)
        fn(self)
        logging.info('done executing {fn}', fn=fn.__name__)

    return fn2


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

        self.started = False
        self.next_valid_order_id = None
        self.global_cancel = False
        self.account = None

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
            print('Contract: ', contract.symbol)
            print('Position: ', position)
            print('Avg Cost: ', avgCost)
            print('Cost Basis: ', position * avgCost)
            print('-----')

    def updatePortfolio(self, contract:Contract, position:float,
                        marketPrice:float, marketValue:float,
                        averageCost:float, unrealizedPNL:float,
                        realizedPNL:float, accountName:str):
        print(contract.symbol, position, unrealizedPNL)

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
            # self.reqContractDetails(1, DirexionSectorBulls.cure())
            # self.reqPositions()
            self.accountOperations_req()

    def accountOperations_req(self):
        self.reqAccountUpdates(True, self.account)

    def accountOperations_cancel(self):
        self.reqAccountUpdates(False, self.account)

    def stop(self):
        logging.info('stopping app')
        self.reqAccountUpdates(False, '')
        self.done = True
        self.disconnect()


def main():
    setupLogger(logging_level=logging.DEBUG)

    logging.info("executing job")

    app = TestApp()
    app.connect(host='127.0.0.1', port=TWS_PORT, clientId=0)

    app.run()
    # app.stop()


if __name__ == '__main__':
    main()
