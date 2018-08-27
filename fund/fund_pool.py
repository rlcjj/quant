import pandas as pd
from datetime import datetime
import os
from quant.param.param import Parameter
from quant.stock.date import Date
from WindPy import w
w.start()


class FundPool(object):

    """
    下载\获取基金池
    load_fund_pool()
    get_fund_pool()
    """

    def __init__(self):

        self.pool_name = 'Fund_Pool'
        self.pool_load_out_path = Parameter().get_load_out_file(self.pool_name)
        self.pool_read_path = Parameter().get_read_file(self.pool_name)

    def load_fund_pool(self, date, name, pool_number, source= "wind_terminal"):

        if source == "wind_terminal":

            date = Date.change_to_str(date)
            data = w.wset("sectorconstituent", "date=%s;sectorid=%s" % (date, pool_number))
            data = pd.DataFrame(data.Data, index=data.Fields).T
            data.date = data.date.map(Date.change_to_str)
        else:
            data = None

        out_sub_path = os.path.join(self.pool_load_out_path, name)
        if not os.path.exists(out_sub_path):
            os.makedirs(out_sub_path)
        file = name + '_' + date + '.csv'
        out_file = os.path.join(out_sub_path, file)
        data.to_csv(out_file)

    def get_fund_pool_code(self, date=None, name=None):

        if name is None:
            name = '基金持仓基准基金池'
        if date is None:
            date = Date().get_normal_date_series(period='Q')[-2]
            print(date)
        date = Date.change_to_str(date)
        out_sub_path = os.path.join(self.pool_load_out_path, name)
        file = name + '_' + date + '.csv'
        out_file = os.path.join(out_sub_path, file)
        data = pd.read_csv(out_file, encoding='gbk', index_col=[0])
        data = data.sort_values(by=['wind_code'], ascending=True)
        data = list(data['wind_code'].values)
        return data

    def get_fund_pool_name(self, date=None, name=None):

        if name is None:
            name = '基金持仓基准基金池'
        if date is None:
            date = Date().get_normal_date_series(period='Q')[-2]
            print(date)
        date = Date.change_to_str(date)
        out_sub_path = os.path.join(self.pool_load_out_path, name)
        file = name + '_' + date + '.csv'
        out_file = os.path.join(out_sub_path, file)
        data = pd.read_csv(out_file, encoding='gbk', index_col=[0])
        data = data.sort_values(by=['wind_code'], ascending=True)
        data = list(data['sec_name'].values)
        return data

    def get_fund_pool_all(self, date=None, name=None):

        if name is None:
            name = '基金持仓基准基金池'
        if date is None:
            date = Date().get_normal_date_series(period='Q')[-1]
            print(date)
        date = Date.change_to_str(date)
        out_sub_path = os.path.join(self.pool_load_out_path, name)
        file = name + '_' + date + '.csv'
        out_file = os.path.join(out_sub_path, file)
        data = pd.read_csv(out_file, encoding='gbk', index_col=[0])
        data = data.sort_values(by=['wind_code'], ascending=True)
        return data

if __name__ == '__main__':

    date = '20180331'
    # fund_pool_wind_dict = {"普通股票型基金": 2001010101000000,
    #                        "偏股混合型基金": 2001010201000000,
    #                        "港股通基金": 1000024255000000,
    #                        "量化基金": 1000023322000000}
    #
    # fund_pool_wind_dict = {"全部开放式基金": "a201010400000000"}
    #
    # for name, pool_number in fund_pool_wind_dict.items():
    #
    #     print(name, pool_number)
    #     FundPool().load_fund_pool(date, name, pool_number)

    data = FundPool().get_fund_pool_code()
    print(data)

