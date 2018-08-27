import pandas as pd
import os
import numpy as np
from quant.param.param import Parameter
from datetime import datetime, time
from quant.stock.stcok_pool import StockPool
from quant.stock.date import Date
from WindPy import w
w.start()


class StockStatic(object):

    """
    下载、得到一些股票常用的性质（上市退市日、交易状态、自由流通市值）
    为了交易使用 所以每天更新

    load_ipo_date()
    get_ipo_date()

    load_trade_status_today()
    get_trade_status_date()

    load_free_market_value_date()
    get_free_market_value_date()

    """

    def __init__(self):
        pass

    @staticmethod
    def load_ipo_date():

        file = Parameter().get_load_out_file("Ipo_Date")
        code_list = StockPool().get_all_stock_code_now()
        code_list_str = ','.join(code_list)
        data = w.wss(code_list_str, "ipo_date, delist_date")
        data = pd.DataFrame(data.Data, index=data.Fields, columns=data.Codes).T
        data["IPO_DATE"] = data["IPO_DATE"].map(lambda x: x.strftime("%Y%m%d"))
        data["DELIST_DATE"] = data["DELIST_DATE"].map(lambda x: x.strftime("%Y%m%d"))
        data["DELIST_DATE"] = data["DELIST_DATE"].map(lambda x: "21000101" if x == "18991230" else x)
        data.to_csv(file)
        print("####################### Loading IPO date %s#################################")

    @staticmethod
    def get_ipo_date():

        file = Parameter().get_read_file("Ipo_Date")
        ipo_date = pd.read_csv(file, encoding='gbk', index_col=[0])
        ipo_date = ipo_date.astype(np.str)
        return ipo_date

    @staticmethod
    def load_trade_status_today():

        today = datetime.today()
        """
        超过9：15 就用今天的数据
        不超过9：15 就用昨天的数据

        """
        if today.time() > time(9, 15):

            today = Date.change_to_str(today)
            code_list = StockPool().get_all_stock_code_now()
            code_list_str = ','.join(code_list)
            print(" Loading Trade Status At ", today)
            trade_status = w.wsq(code_list_str, "rt_trade_status")
            trade_status_pd = pd.DataFrame(trade_status.Data, index=['Trade_Status'], columns=trade_status.Codes).T
            out_path = Parameter().get_read_file("Trade_Status")
            trade_status_pd = trade_status_pd[(trade_status_pd['Trade_Status'] != 1.0) & (trade_status_pd['Trade_Status'] != 4.0)]

            if len(trade_status_pd) > 1000:
                trade_status = w.wss(code_list_str, "trade_status", "tradeDate=" + today)
                trade_status_pd = pd.DataFrame(trade_status.Data, index=['Trade_Status'], columns=trade_status.Codes).T
                trade_status_pd = trade_status_pd[trade_status_pd['Trade_Status'] != "交易"]
                out_path = Parameter().get_read_file("Trade_Status")
                out_file = os.path.join(out_path, 'trade_status_' + today + '.csv')
                trade_status_pd.to_csv(out_file)
            else:
                out_file = os.path.join(out_path, 'trade_status_' + today + '.csv')
                trade_status_pd.to_csv(out_file)

        else:
            today = Date.change_to_str(today)
            before_date = Date().get_trade_date_offset(today, -1)
            code_list = StockPool().get_all_stock_code_now()
            code_list_str = ','.join(code_list)
            print(" Loading Trade Status At ", before_date)
            trade_status = w.wss(code_list_str, "trade_status", "tradeDate=" + before_date)
            trade_status_pd = pd.DataFrame(trade_status.Data, index=['Trade_Status'], columns=trade_status.Codes).T
            trade_status_pd = trade_status_pd[trade_status_pd['Trade_Status'] != "交易"]
            out_path = Parameter().get_read_file("Trade_Status")
            out_file = os.path.join(out_path, 'trade_status_' + today + '.csv')
            trade_status_pd.to_csv(out_file)

    @staticmethod
    def get_trade_status_date(date):

        date = Date.change_to_str(date)
        out_path = Parameter().get_read_file("Trade_Status")
        out_file = os.path.join(out_path, 'trade_status_' + date + '.csv')
        trade_status = pd.read_csv(out_file, index_col=[0], encoding='gbk')
        return trade_status

    @staticmethod
    def load_free_market_value_date(date):

        date = Date.change_to_str(date)
        out_path = Parameter().get_load_out_file("Free_Market_Value")
        code_list = StockPool().get_all_stock_code_now()
        code_list_str = ','.join(code_list)
        data = w.wss(code_list_str,  "mkt_freeshares", "unit=1;tradeDate=" + date)
        data = pd.DataFrame(data.Data, index=['Free_Market_Value'], columns=data.Codes).T
        out_file = os.path.join(out_path, "Free_Market_Value_" + date + '.csv')
        data.to_csv(out_file)
        print("####################### Loading Free_Market_Value At %s#################################" % date)

    @staticmethod
    def get_free_market_value_date(date):

        date = Date.change_to_str(date)
        out_path = Parameter().get_read_file("Free_Market_Value")
        out_file = os.path.join(out_path, 'Free_Market_Value_' + date + '.csv')
        free_market_value = pd.read_csv(out_file, index_col=[0], encoding='gbk')
        return free_market_value


if __name__ == '__main__':

    ################################################################################
    date = datetime(2018, 7, 6)
    # StockStatic().load_trade_status_today()
    # print(StockStatic().get_trade_status_date(date))
    #
    # StockStatic().load_free_market_value_date(date)
    # print(StockStatic().get_free_market_value_date(date))

    StockStatic().load_ipo_date()
    print(StockStatic().get_ipo_date())
    ################################################################################