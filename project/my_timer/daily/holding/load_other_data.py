from quant.mfc.mfc_data import MfcData
from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.stock.index import Index
from datetime import datetime

"""
下载昨日收盘的指数权重 300 500 财富大盘(FTP) \ 50 万德全A等其他(wind)
下载今日的停牌股票 9:15前 wss "trade_status" \ 9:15后 wsq "rt_trade_status"
下载股票池
下载今日的股票上市日期
下载昨天股票自由流通市值 用以计算 China Index Benchmark
"""


def load_other_data(today):

    # 交易日更新
    Date().load_trade_date_series("D")
    # today = datetime.today().strftime("%Y%m%d")
    before_trade_date = Date().get_trade_date_offset(today, -1)

    # 下载指数权重
    Index().load_weight_from_ftp_date("000300.SH", before_trade_date)
    Index().load_weight_from_ftp_date("000905.SH", before_trade_date)
    Index().load_weight_from_ftp_date("000940.SH", before_trade_date)

    Index().load_weight_from_wind_date("000016.SH", before_trade_date)
    Index().load_weight_from_wind_date("881001.WI", before_trade_date)

    # 下载股票池
    Stock().load_all_stock_code_now()

    # 下载上市日期
    Stock().load_ipo_date()

    # 下载停牌股票
    Stock().load_trade_status_today()

    # 下载昨天股票自由流通市值 用以计算 China Index Benchmark
    Stock().load_free_market_value_date(before_trade_date)
    Index().load_weight_china_index_date(before_trade_date)


if __name__ == '__main__':

    today = datetime.today()
    today = datetime(2018, 7, 6)
    load_other_data(today)
