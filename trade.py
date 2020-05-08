from tda import auth
import requests
import csv
import json
import pandas
import datetime


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

r = c.get_price_history('AAL',
        period_type=c.PriceHistory.PeriodType.YEAR,
        period=c.PriceHistory.Period.TWENTY_YEARS,
        frequency_type=c.PriceHistory.FrequencyType.DAILY,
        frequency=c.PriceHistory.Frequency.DAILY)
assert r.ok, r.raise_for_status()


r = c.get_quote("SPXL")
d = json.loads(r.text)
#f = d['closePrice']
print(json.dumps(r.json(), indent=4))

names = extract_values(r.json(), 'closePrice')
print(names)

