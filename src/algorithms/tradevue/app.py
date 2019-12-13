import os
import logging
import datetime
import hashlib

from google.cloud import firestore

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.ticktype import TickTypeEnum

from common.utils.logging import setupLogger


class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

        self.ts = datetime.datetime.now().__format__('%Y-%m-%d-%H-%M-%S')
        self.started = False
        self.next_valid_order_id = None
        self.global_cancel = False
        self.account = None
        self.positions = {}
        self.contracts = []
        self.symbol_hash_map = {}
        self.db = firestore.Client()

    def error(self, reqId, errorCode, errorString):
        if errorCode != 2104:
            print("Error: ", reqId, " ", errorCode, " ", errorString)

    # def start(self):
    #     if self.started:
    #         return
    #     self.started = True

    #     if self.global_cancel:
    #         logging.info('executing global cancel')
    #         self.reqGlobalCancel()
    #     else:
    #         logging.info('executing requests')
    #         self.reqPositions()
    #         self.reqAccountUpdates(True, self.account)

    # def stop(self):
    #     logging.info('stopping app')
    #     self.reqAccountUpdates(False, '')
    #     self.done = True
    #     self.disconnect()

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        print('')
        logging.debug("setting next_valid_order_id: {o}".
                      format(o=orderId))
        self.next_valid_order_id = orderId
        # self.start()

    def tickPrice(self, reqId, tickType, price, attrib):
        if price >= 0.0:
            print("Tick Price.", self.symbol_hash_map[reqId], price)

    def position(self, account, contract, position, avgCost):
        payload = {
            'contract': {
                'contract_id': contract.conId,
                'symbol': contract.symbol,
                'security_type': contract.secType,
                'last_trade_date': contract.lastTradeDateOrContractMonth,
                'strike': contract.strike,
                'multiplier': contract.multiplier,
                'primary_exchange': contract.primaryExchange,
                'exchange': contract.exchange,
                'currency': contract.currency
            },
            'position': {
                'position_qty': position,
                'avg_cost': avgCost,
                'cost_basis': position * avgCost,
            },
            'audit': {
                'ts': self.ts
            }
        }
        self.db.collection(u'portfolio'). \
            document(contract.symbol). \
            set(payload)

        hash_id = int(
            hashlib.sha256(contract.symbol.encode('utf-8')).hexdigest(), 16
        ) % 10**8

        print(contract.symbol, hash_id)

        self.symbol_hash_map[hash_id] = contract.symbol

        self.reqMarketDataType(1)
        self.reqMktData(hash_id, contract, "", False, False, [])
        #TODO: Push to service that can handle rendering
        #TODO: Push to service that can retrieve market data


def main():
    setupLogger(logging_level=logging.INFO)

    TWS_PORT = int(os.getenv('TWS_PORT'))

    app = TestApp()

    app.connect(host='127.0.0.1', port=TWS_PORT, clientId=0)

    app.reqPositions()

    app.run()

    # pos = app.positions
    # app.reqMarketDataType(1)
    # app.reqMktData(1, contract, "", False, False, [])


if __name__ == "__main__":
    main()
