from ibapi.contract import Contract


def make_contract(symbol: str, exchange: str, secType: str):
    contract = Contract()
    contract.symbol = symbol
    contract.exchange = exchange
    contract.secType = secType
    contract.currency = 'USD'
