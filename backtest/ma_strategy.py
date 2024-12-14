# *_* coding : UTF-8 *_*
# 开发团队  ：  LiYan
# 开发人员  ：  LiYan
# 开发时间  ：  2024/12/14  20:21
# 文件名称  :  ma_strategy.py.PY
# 开发工具  :  PyCharm
#d81925c2980896a99dcc5c4f2044bdbf883d99af0833f37d14cfbec6
# -*- coding: UTF-8 -*-
# 开发团队  ：  LiYan
# 开发人员  ：  LiYan
# 开发时间  ：  2024/12/14  20:21
# 文件名称  :  ma_strategy.py.PY
# 开发工具  :  PyCharm
import backtrader as bt
import datetime
import tushare as ts
import sys
import pandas as pd

class MAStrategy(bt.Strategy):
    params = (
        ('short_window', 12),
        ('long_window', 26),
        ('slippage', 0.0001),  # 万分之一滑点
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None

        # 设置滑点
        self.broker.set_slippage_fixed(self.params.slippage)

        # 初始化均线指标
        self.sma_short = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.short_window)
        self.sma_long = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.long_window)

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.sma_short[0] > self.sma_long[0]:
                size = int(0.2 * self.broker.getvalue() / self.dataclose[0])
                self.order = self.buy(size=size)
        else:
            if self.dataclose[0] < self.sma_long[0]:
                self.order = self.sell()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                print(f'BUY EXECUTED, Price: {order.executed.price}, Cost: {order.executed.value}, Comm: {order.executed.comm}')
            elif order.issell():
                print(f'SELL EXECUTED, Price: {order.executed.price}, Cost: {order.executed.value}, Comm: {order.executed.comm}')

        self.order = None

def run_backtest(stock_code, start_date, end_date, initial_cash=1000000):
    cerebro = bt.Cerebro()

    # 添加策略
    cerebro.addstrategy(MAStrategy)

    # 将开始日期提前一些天数，确保有足够的数据
    start_date_extended = (pd.to_datetime(start_date) - pd.Timedelta(days=MAStrategy.params.long_window * 2)).strftime('%Y%m%d')

    # 下载数据
    pro = ts.pro_api('e3b70360985a340bc905bf20e3c74bc6cbf7fa862febe1ece11fd3d4')  # 替换为你的 Tushare Token
    df = pro.daily(ts_code=stock_code, start_date=start_date_extended, end_date=end_date)
    df['date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
    df.set_index('date', inplace=True)

    # 调试信息：打印下载的数据
    print(f"Downloaded data from {df.index.min()} to {df.index.max()}")
    print(f"Number of trading days: {len(df)}")

    # 检查数据长度是否足够
    if len(df) < MAStrategy.params.long_window:
        raise ValueError(f"数据长度不足，需要至少 {MAStrategy.params.long_window} 天的数据")

    data = bt.feeds.PandasData(dataname=df)

    # 添加数据
    cerebro.adddata(data)

    # 设置初始资金
    cerebro.broker.setcash(initial_cash)

    # 运行回测
    cerebro.run()

    # 返回最终权益
    final_value = cerebro.broker.getvalue()
    total_return = (final_value - initial_cash) / initial_cash

    return total_return, final_value

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python ma_strategy.py <stock_code> <start_date> <end_date>")
        sys.exit(1)

    stock_code = sys.argv[1]
    start_date = sys.argv[2]
    end_date = sys.argv[3]
    try:
        total_return, final_value = run_backtest(stock_code, start_date, end_date)
        print(f'Total Return: {total_return:.2%}')
        print(f'Final Value: {final_value}')
    except Exception as e:
        print(f'Error: {e}')



















