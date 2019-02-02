import os
import logging
import time

from ibapi import wrapper
from ibapi.client import EClient
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
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)


class TestWrapper(wrapper.EWrapper):
    def __init__(self):
        wrapper.EWrapper.__init__(self)


class TestApp(TestWrapper, TestClient):
    def __init__(self):
        TestWrapper.__init__(self)
        TestClient.__init__(self, wrapper=self)

        self.started = False
        self.next_valid_order_id = None
        self.global_cancel = False
        self.num_keyb_int = 0

    @iswrapper
    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        logging.debug("setting next_valid_order_id: {o}".
                      format(o=orderId))
        self.next_valid_order_id = orderId
        self.start()

    def nextOrderId(self):
        oid = self.next_valid_order_id
        self.next_valid_order_id += 1
        return oid

    def keyboardInterrupt(self):
        self.num_keyb_int += 1
        if self.num_keyb_int == 1:
            logging.info('keyboard interrupt stopping app')
            self.stop()
        else:
            print("Finishing test")
            self.done = True

    def start(self):
        if self.started:
            return
        self.started = True

        if self.global_cancel:
            logging.info('executing global cancel')
            self.reqGlobalCancel()
        else:
            logging.info('executing requests')
            self.reqContractDetails(1, DirexionSectorBulls.cure())

    def stop(self):
        logging.info('stopping app')
        self.done = True
        self.disconnect()

    @iswrapper
    def error(self, reqId, errorCode: int, errorString: str):
        super().error(reqId, errorCode, errorString)

    def contractDetails(self, reqId, contractDetails):
        print('Request ID: ', reqId)
        print('Contract: ', contractDetails.contract.symbol)
        print('Long Name: ', contractDetails.longName)


def main():
    setupLogger(logging_level=logging.ERROR)

    logging.info("executing job")

    app = TestApp()
    app.connect(host='127.0.0.1', port=TWS_PORT, clientId=0)

    app.run()
    app.stop()


if __name__ == '__main__':
    main()
