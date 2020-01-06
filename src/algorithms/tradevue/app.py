import logging
import datetime
import hashlib

from google.cloud import firestore

from ibapi.client import EClient
from ibapi.wrapper import EWrapper

from common.utils.logging import setupLogger
from common.data_handler import ftp

db = firestore.Client()


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
        # self.db = firestore.Client()

    def error(self, reqId, errorCode, errorString):
        if errorCode != 2104:
            print("Error: ", reqId, " ", errorCode, " ", errorString)

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        print('')
        logging.debug("setting next_valid_order_id: {o}".
                      format(o=orderId))
        self.next_valid_order_id = orderId

    def tickString(self, reqId, tickType, value: str):
        symbol = self.symbol_hash_map[reqId]
        print(symbol, value)

    def tickPrice(self, reqId, tickType, price, attrib):
        symbol = self.symbol_hash_map[reqId]
        if price >= 0.0:
            payload = {
                'current_price.price':  price,
                'current_price.ts': datetime.datetime.now().strftime("%s")
            }

            db.collection(u'portfolio'). \
                document(symbol). \
                update(payload)

            print(symbol, price)

    def tickSize(self, reqId, tickType, size):
        pass

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
            'current_price': {
                'price': None,
                'ts': None
            }
        }
        db.collection(u'portfolio'). \
            document(contract.symbol). \
            set(payload)

        hash_id = int(
            hashlib.sha256(contract.symbol.encode('utf-8')).hexdigest(), 16
        ) % 10**8

        print(contract.symbol, hash_id)

        self.symbol_hash_map[hash_id] = contract.symbol

        self.reqMarketDataType(1)
        self.reqMktData(hash_id, contract, "", False, False, [])


def main():
    setupLogger(logging_level=logging.INFO)

    # Retrieve latest FTP data and post to firebase
    try:
        ftp_data = ftp.get_data()
        logging.info('FTP data retrieved successfully')

        for report_type in ftp_data.keys():
            db.collection('static').document(report_type).set(ftp_data[report_type])

    except:
        Exception('Unable to retrieve latest batch from FTP')

    # Run TWS Client
    try:
        import os
        TWS_PORT = int(os.getenv('TWS_PORT'))
        app = TestApp()
        app.connect(host='127.0.0.1', port=TWS_PORT, clientId=0)
        app.reqPositions()
        app.run()
    except:
        Exception('Unable to run TWS client')


if __name__ == "__main__":
    main()
