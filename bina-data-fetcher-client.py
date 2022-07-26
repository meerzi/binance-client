# coding=utf-8
# standard module import
import pandas
import requests
import time

# 3rd party module import
from prometheus_client import start_http_server, Gauge


class BinaDataFetcherClient:

    BINANCE_API_URL = 'https://api.binance.com/api'

    def __init__(self):
        self.BINANCE_API_URL = self.BINANCE_API_URL
        self.prometheus_gauge = Gauge('absolute_delta_value',
                        'Absolute Delta Value of Price Spread', ['symbol'])

    def health_check(self):
        """check health of Binance API"""
        uri_path = "/v3/ping"

        r = requests.get(self.BINANCE_API_URL + uri_path)

        if r.status_code != 200:
            raise Exception("Binance API is not reachable.")

    def get_top_symbols(self, asset, field, result=False):
        """
        Return the top 5 symbols with quote asset BTC
        and the highest volume over the last 24 hours
        in descending order in data frames.
        """
        uri_path = "/v3/ticker/24hr"

        r = requests.get(self.BINANCE_API_URL + uri_path)
        data_frame = pandas.DataFrame(r.json())
        data_frame = data_frame[['symbol', field]]
        data_frame = data_frame[data_frame.symbol.str.contains(r'(?!$){}$'.format(asset))]
        data_frame[field] = pandas.to_numeric(data_frame[field], downcast='float', errors='coerce')
        data_frame = data_frame.sort_values(by=[field], ascending=False).head(5)

        if result:
            print(data_frame)

        return data_frame

    def get_notional_value(self, asset, field, result=False):
        """
        Return the total notional value of the
        200 bids and asks on each symbol's order book
        in dictionary format.

        {
          'SCBTC_bids': 150.36464938999989,
          'SCBTC_asks': 140.73872424,
          'VETBTC_bids': 208.85985879998888,
          'VETBTC_asks': 98.65120531997777
        }
        """
        uri_path = "/v3/depth" 

        symbols = self.get_top_symbols(asset, field, result=False)
        notional_list = {}

        for s in symbols['symbol']:
            payload = { 'symbol' : s, 'limit' : 500 }
            r = requests.get(self.BINANCE_API_URL + uri_path, params=payload)
            for col in ["bids", "asks"]:
                data_frame = pandas.DataFrame(data=r.json()[col], columns=["price", "quantity"], dtype=float)
                data_frame = data_frame.sort_values(by=['price'], ascending=False).head(200)
                data_frame['notional'] = data_frame['price'] * data_frame['quantity']
                data_frame['notional'].sum()
                notional_list[s + '_' + col] = data_frame['notional'].sum()

        if result:
            print(notional_list)

        return notional_list

    def get_price_spread(self, asset, field, result=False):
        """
        Return the price spread for each symbols in dictionary format

        {
          'BTCUSDT': 0.021000000002037277,
          'ETHUSDT': 0.08899999999992755,
          'CHZUSDT': 0.00043999999999999276,
          'ALICEUSDT': 0.05270000000000082,
          'BNBUSDT': 0.2047999999999987
        }

        """

        uri_path = '/v3/ticker/bookTicker'

        symbols = self.get_top_symbols(asset, field)
        spread_map = {}

        for s in symbols['symbol']:
            payload = { 'symbol' : s }
            r = requests.get(self.BINANCE_API_URL + uri_path, params=payload)
            price_spread = r.json()
            spread_map[s] = float(price_spread['askPrice']) - float(price_spread['bidPrice'])
 
        if result:
            print(spread_map)

        return spread_map

    def get_spread_delta(self, asset, field, result=False):

        spread_delta = {}
        old_spread = self.get_price_spread(asset, field)
        # 
        time.sleep(10)
        new_spread = self.get_price_spread(asset, field)

        for key in old_spread:
            spread_delta[key] = abs(old_spread[key]-new_spread[key])

        for key in spread_delta:
            self.prometheus_gauge.labels(key).set(spread_delta[key])

        if result:
            print(spread_delta)


if __name__ == "__main__":
    # server to expose the metrics in Prometheus Metrix Format.
    start_http_server(8080)
    client = BinaDataFetcherClient()
    client.health_check()

    # To Print Details
    print()
    print("Top 5 symbols with quote asset BTC and the highest volume over the last 24 hours in descending order")
    print()
    client.get_top_symbols('BTC', 'volume', True)
    print()

    print("Top 5 symbols with quote asset USDT and the highest number of trades over the last 24 hours in descending order")
    print()
    client.get_top_symbols('USDT', 'count', True)
    print()

    print("Total notional value of the top 200 bids and asks currently on each order book")
    print()
    client.get_notional_value('BTC', 'volume', True)
    print()

    print("Price spread for each of the symbols from Q2")
    print()
    client.get_price_spread('USDT', 'count', True)
    print()

    while True:
        print("Result of Q4 and the absolute delta from the previous value for each symbol")
        print()
        client.get_spread_delta('USDT', 'count', True)
        print()
