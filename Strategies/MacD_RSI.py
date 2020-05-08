import math
import backtrader as bt


class MacD_RSI(bt.Strategy):
    params = {
        ('fast', 12),
        ('slow', 26),
        ('macdsig', 9),
        ('atrperiod', 14),
        ('atrdist', 3.0),
        ('smaperiod', 30),
        ('order_percentage', 0.95),
        ('dirperiod', 10),
        ('ticker', 'SPY')
    }
    lines = ('macd', 'signal', 'histo')

    def get_order_price(self):
        return self.orderprice

    def set_order_price(self, price):
        self.orderprice = price

    def log(self, txt, dt=None):
        """ Logging function fot this strategy"""
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self, orderprice=0.00):
        self.orderprice = orderprice
        # self.fast_moving_average = EMA(
        #     self.data.close, period=self.params.fast, plotname='12 day moving average'
        # )
        #
        # self.slow_moving_average = EMA(
        #     self.data.close, period=self.params.slow, plotname='26 day moving average'
        # )

        # self.lines.macd = self.fast_moving_average - self.slow_moving_average
        # self.lines.signal = EMA(self.lines.macd, period=self.params.macdsig)
        # self.lines.histo = self.lines.macd - self.lines.signal

        self.bband = bt.indicators.BollingerBands()
        self.rsi = bt.indicators.RelativeStrengthIndex()

        self.rsi_buy_enable = None
        self.rsi_sell_enable = None
        self.rsi_strong_buy = None
        self.rsi_strong_sell = None
        self.bar_executed = None
        self.order = None
        self.size = None
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:

            if order.isbuy():
                self.log('BUY EXECUTED {}'.format(order.executed.price))
                self.bar_executed = len(self)
            elif order.issell():
                self.log('SELL EXECUTED {}'.format(order.executed.price))

        self.set_order_price(order.executed.price)

        self.order = None

    def next(self):
        self.log('Close, %.2f' % self.data.close[0])

        if self.rsi[0] < 30:
            self.rsi_buy_enable = True

        if self.rsi[0] > 30 and self.rsi_sell_enable:
            self.rsi_strong_buy = True

        if self.rsi[0] > 70:
            self.rsi_sell_enable = True

        if self.rsi[0] < 70 and self.rsi_sell_enable:
            self.rsi_strong_sell = True

        print("strong buy = " + str(self.rsi_strong_buy))
        print("strong sell = " + str(self.rsi_strong_sell))
        print("rsi = " + str(self.rsi[0]))

        if self.position.size == 0:

            if (self.rsi_strong_buy == 1 and
                    self.bband.lines.bot[0] > self.data.close[0] and
                    self.data.volume[0] > 50000):

                amount_to_invest = (self.broker.cash * self.params.order_percentage)
                self.size = math.floor(amount_to_invest / self.data.close)

                print("Buy {} shares of {} at {}".format(self.size, self.params.ticker, self.data.close[0]))
                self.log('BUY CREATE, %.2f' % self.data.close[0])
                self.order = self.buy(size=self.size)

                self.rsi_strong_buy = False
                self.rsi_buy_enable = False
            else:
                self.rsi_strong_buy = False
                self.rsi_buy_enable = False

        if self.position.size > 0:

            loss = self.data.close[0] - self.orderprice
            gain = self.orderprice - self.data.close[0]

            if (self.rsi_strong_sell == 1 or
                    loss > self.data.close[0] * .01 or
                    gain > self.data.close[0] * .04 and
                    self.data.volume[0] > 70000):
                print("Sell {} shares of {} at {}".format(self.size, self.params.ticker, self.data.close[0]))
                self.log('SELL CREATED {}'.format(self.data.close[0]))
                self.order = self.close()

                self.rsi_strong_sell = False
                self.rsi_sell_enable = False
