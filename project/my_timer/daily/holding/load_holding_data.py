from quant.mfc.mfc_data import MfcData
from datetime import datetime
from quant.stock.date import Date

"""
下载 昨日的持仓数据 包括 基金资产 基金证券 组合证券 成交回报 委托流水 单元资产
     昨日的股票库   包括 公司 量化 和 各个基金 的股票库
"""


def load_mfc_holding_data(today):

    lmd = MfcData()
    # today = datetime.today()
    # today = datetime(2018, 6, 27).strftime("%Y%m%d")

    lmd.load_holding_date(date=today)
    lmd.load_stock_pool_date(date=today)
    lmd.change_holding_date(date=today)


if __name__ == '__main__':

    today = datetime.today()
    load_mfc_holding_data(today)