import os
from datetime import datetime
import pandas as pd
from quant.fund.fund_static import FundStatic
from quant.fund.fund_pool import FundPool
from quant.data_source.fin_db import FinDb
from quant.param.param import Parameter
from quant.stock.date import Date
from quant.utility_fun.pandas_fun import pandas_add_row


class FundFactor(object):

    """
    下载、读取基金因子数据
    load_fund_factor()
    get_fund_factor()
    """

    def __init__(self):
        pass

    def load_fund_factor(self, factor_name, beg_date, end_date):

        beg_date = Date().change_to_str(beg_date)
        end_date = Date().change_to_str(end_date)
        new_data = FinDb().load_raw_data_filter_period(factor_name, beg_date, end_date)
        fund_info_data = FundStatic().get_fund_info()
        val_name = Parameter().get_load_findb_val_name(factor_name)

        new_data = pd.merge(new_data, fund_info_data, on="证券内码", how='inner')
        new_data = pd.DataFrame(new_data[val_name].values, index=[list(new_data['基金代码'].values),
                                                           list(new_data['日期'].values)])
        new_data = new_data.sort_index()
        new_data = new_data[~new_data.index.duplicated()]
        new_data = new_data.unstack()

        new_data.columns = new_data.columns.droplevel(level=0)
        new_data = new_data.T
        new_data = new_data.dropna(how='all')
        new_data.index = new_data.index.map(str)

        out_file = Parameter().get_read_file(factor_name)
        if os.path.exists(out_file):
            data = pd.read_csv(out_file, encoding='gbk', index_col=[0])
            data.index = data.index.map(str)
            data = pandas_add_row(data, new_data)
        else:
            print(" File No Exist ", factor_name)
            data = new_data
        data = data.dropna(how='all')
        data.to_csv(out_file)

    def get_fund_factor(self, factor_name, date_list=None, fund_pool=None):

        out_file = Parameter().get_read_file(factor_name)
        data = pd.read_csv(out_file, index_col=[0], encoding='gbk')
        data.index = data.index.map(str)
        if date_list is not None:
            data = data.ix[date_list, :]
        if fund_pool is not None:
            data = data.ix[:, fund_pool]

        return data


if __name__ == '__main__':

    # load factor
    ###################################################################################
    # FundFactor().load_fund_factor("Unit_Nav", "19991231", datetime.today())
    # FundFactor().load_fund_factor("Acc_Nav", "19991231", datetime.today())
    # FundFactor().load_fund_factor("Repair_Nav", "19991231", datetime.today())
    # FundFactor().load_fund_factor("Repair_Nav_Pct", "19991231", datetime.today())
    FundFactor().load_fund_factor("Total_Asset", "19991231", datetime.today())
    FundFactor().load_fund_factor("Stock_Ratio", "19991231", datetime.today())
    FundFactor().load_fund_factor("Fixed_Ratio", "19991231", datetime.today())

    # get factor
    ###################################################################################
    # FundPool = FundPool().get_fund_pool_code()
    # DateSeries = Date().get_trade_date_series("20180101", datetime.today())
    # print(FundPool, DateSeries)
    # data = FundFactor().get_fund_factor("Repair_Nav", DateSeries, FundPool)
    # print(data)


