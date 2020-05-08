import backtrader
import json
import datetime
from Strategies.MacD_RSI import MacD_RSI
from tda import auth
import pandas
import csv


cerebro = backtrader.Cerebro()

cerebro.broker.set_cash(1000.00)

token_path = 'token'
api_key = '3GMQOGDPBEZLRPSBIKBVCQILWQWE8KD6@AMER.OAUTHAP'
redirect_uri = 'https://localhost'
try:
    c = auth.client_from_token_file(token_path, api_key)
except FileNotFoundError:
    from selenium import webdriver

    options = webdriver.ChromeOptions()
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ['enable-automation'])

    with webdriver.Chrome(chrome_options=options, executable_path='C:/Users/stacy/Desktop/chromedriver_win32/chromedriver.exe') as driver:
        c = auth.client_from_login_flow(
            driver, api_key, redirect_uri, token_path)


r = c.get_price_history('SPXL',
                           period_type=c.PriceHistory.PeriodType.DAY,
                           period=c.PriceHistory.Period.TEN_DAYS,
                           frequency_type=c.PriceHistory.FrequencyType.MINUTE,
                           frequency=c.PriceHistory.Frequency.EVERY_MINUTE
                        )
assert r.ok, r.raise_for_status()
#print(json.dumps(r.json(), indent=4))

data_r = r.json()['candles']

count = 1
for candle in data_r:
    candle['datetime'] = pandas.to_datetime(candle['datetime'], unit='ms')

with open ('data_file.csv','w') as f:
    csv_writer = csv.writer(f)

    count = 0

    for candle in data_r:
        if count == 0:
            # Writing headers of CSV file
            header = candle.keys()
            csv_writer.writerow(header)
            count += 1

        # Writing data of CSV file
        csv_writer.writerow(candle.values())

pd_data = pandas.read_csv('data_file.csv', index_col='datetime', parse_dates=True)

data = backtrader.feeds.PandasData(dataname=pd_data)

cerebro.adddata(data)

cerebro.addstrategy(MacD_RSI)

cerebro.addsizer(backtrader.sizers.FixedSize, stake=30)


print('Starting value: %.2f' % cerebro.broker.getvalue())

cerebro.run()

print('Final Value: %2f' % cerebro.broker.getvalue())

cerebro.plot()

