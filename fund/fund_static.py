import pandas as pd
from datetime import datetime
import numpy as np
import os
from quant.param.param import Parameter
from quant.data_source.fin_db import FinDb
from quant.stock.date import Date
from quant.fund.fund_pool import FundPool
from quant.utility_fun.code_format import stock_code_add_postfix, fund_code_add_postfix
from WindPy import w
w.start()


class FundStatic(object):

    def __init__(self):
        pass

    @staticmethod
    def if_a_fund(x):

        if ('C' in x) or ('O' in x) or ('H' in x) or ('I' in x) or ('B' in x) or ('D' in x) or ('E' in x) or ('R' in x):
            return '非A类基金'
        else:
            return 'A类基金'

    def load_wind_fund_asset(self, date=None):

        if date is None:
            date = Date().get_normal_date_series(period='Q')[-2]
            print(date)

        code = FundPool().get_fund_pool_code(date, "基金持仓基准基金池")
        code_str = ','.join(list(code))
        data = w.wss(code_str, "prt_fundnetasset_total", "unit=1;rptDate=" + str(date))
        data = pd.DataFrame(data.Data, columns=data.Codes, index=["FundAsset"]).T
        out_path = Parameter().get_load_out_file("Fund_Asset")
        out_file = "基金规模_" + date + '.csv'
        out_file = os.path.join(out_path, out_file)
        data.to_csv(out_file)

    def get_wind_fund_asset(self, date=None):

        if date is None:
            date = Date().get_normal_date_series(period='Q')[-2]
            print(date)

        date = Date.change_to_str(date)
        out_path = Parameter().get_read_file("Fund_Asset")
        out_file = "基金规模_" + date + '.csv'
        out_file = os.path.join(out_path, out_file)
        data = pd.read_csv(out_file, encoding='gbk', index_col=[0])
        return data

    def load_sec_info(self, pool_name=101):

        data = FinDb().load_raw_data_filter("Sec_Basic_Info", pool_name)
        data['证券代码'] = data['证券代码'].map(stock_code_add_postfix)
        out_file = Parameter().get_load_findb_out_file("Sec_Basic_Info")
        print(" Loading Security Basic InFo " + out_file)
        data.to_csv(out_file)

    def load_fund_info(self):

        data = FinDb().load_raw_data("Fund_Basic_Info")
        out_file = Parameter().get_load_findb_out_file("Fund_Basic_Info")
        data['基金代码'] = data['基金代码'].map(fund_code_add_postfix)
        print(" Loading Fund Basic InFo " + out_file)
        data.to_csv(out_file)

    @staticmethod
    def get_sec_info():

        file = Parameter().get_read_file("Sec_Basic_Info")
        data = pd.read_csv(file, index_col=[0], encoding='gbk')
        data = data.astype(np.str)
        return data

    @staticmethod
    def get_fund_info():

        file = Parameter().get_read_file("Fund_Basic_Info")
        data = pd.read_csv(file, index_col=[0], encoding='gbk')
        data = data.astype(np.str)
        return data

if __name__ == '__main__':

    # date_series = Date().get_normal_date_series("20040101", datetime.today())
    # for i_date in range(0, len(date_series) - 1):
    #     report_date = date_series[i_date]
    #     FundStatic().load_wind_fund_asset(report_date)

    # FundStatic().load_sec_info()
    # FundStatic().load_fund_info()

    FundStatic().load_wind_fund_asset()
    FundStatic().get_wind_fund_asset()

