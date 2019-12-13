import os
import logging
import datetime

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
        print("Tick Price. Ticker Id:", reqId,
              "tickType:", "Price:", price, attrib)

    def position(self, account: str, contract: Contract, position: float,
                 avgCost: float):
        payload = {
            'contract': {
                'con_id': contract.conId,
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
        self.positions[contract.symbol] = payload
        if contract.conId not in self.contracts:
            self.contracts.append(contract.conId)
        print(payload, self.positions, self.contracts)


def main():
    setupLogger(logging_level=logging.INFO)

    TWS_PORT = int(os.getenv('TWS_PORT'))

    app = TestApp()

    app.connect(host='127.0.0.1', port=TWS_PORT, clientId=0)

    contract = Contract()
    contract.symbol = 'CHWY'
    contract.secType = 'STK'
    contract.exchange = 'NYSE'
    contract.currency = 'USD'

    app.reqPositions()

    app.reqMarketDataType(1)
    app.reqMktData(1, contract, "", False, False, [])

    app.run()


if __name__ == "__main__":
    main()
