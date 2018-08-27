from datetime import datetime
import numpy as np
import pandas as pd
from quant.data_source.fin_db import FinDb
from quant.param.param import Parameter
from quant.stock.date import Date
from quant.fund.fund_static import FundStatic


class FundHolder(object):

    def __init__(self):

        self.holder_name = "Fund_Stock_Holding"

    def load_fund_holding(self, beg_date, end_date):

        beg_date = Date().change_to_str(beg_date)
        end_date = Date().change_to_str(end_date)
        new_data = FinDb().load_raw_data_filter_period(self.holder_name, beg_date, end_date)
        fund_info_data = FundStatic().get_fund_info()
        fund_info_data = fund_info_data.rename(columns={"证券内码": "基金内码", "证券代码": "基金代码"})
        stock_info_data = FundStatic().get_sec_info()
        stock_info_data = stock_info_data.rename(columns={"证券内码": "股票内码", "证券代码": "股票代码"})
        stock_info_data = stock_info_data.ix[:, ["股票内码", "股票代码"]]

        new_data = pd.merge(new_data, fund_info_data, on="基金内码", how='inner')
        new_data = pd.merge(new_data, stock_info_data, on="股票内码", how='inner')
        new_data = new_data[["发布日期", "截至日期", "基金代码", "基金简称",
                             "股票代码", "股票名称", "占净值比", "持仓股数", "持仓市值"]]
        new_data = new_data.sort_values(by=["截至日期", "基金代码", "股票代码"], ascending=True)
        Index = pd.MultiIndex.from_arrays(new_data[["截至日期", "基金代码", "股票代码"]].T.values,
                                          names=["截至日期", "基金代码", "股票代码"])
        data = pd.DataFrame(new_data[["发布日期", "基金简称", "股票名称",
                                      "占净值比", "持仓股数", "持仓市值"]].values, index=Index,
                                columns=["发布日期", "基金简称", "股票名称",
                                        "占净值比", "持仓股数", "持仓市值"])

        out_file = Parameter().get_load_findb_out_file(self.holder_name)
        data.to_csv(out_file)

    def get_fund_holding_all(self):

        file = Parameter().get_read_file(self.holder_name)
        fund_holding = pd.read_csv(file, encoding='gbk')

        fund_holding = fund_holding[['基金代码', '股票代码', '占净值比', '截至日期']]
        fund_holding.columns = ['FundCode', 'StockCode', 'Weight', 'Date']
        fund_holding['Date'] = fund_holding['Date'].map(np.str)
        fund_holding = fund_holding.dropna()
        fund_holding = fund_holding.reset_index(drop=True)

        return fund_holding

    def get_fund_holding_report_date(self, report_date=None):

        if report_date is None:
            date_series = Date().get_normal_date_series(beg_date=None, end_date=datetime.today(), period='Q')
            report_date = date_series[-2]

        data = self.get_fund_holding_all()
        data_date = data[data['Date'] == report_date]
        data_date = data_date.reset_index(drop=True)
        return data_date

    def get_fund_holding_one_fund(self, fund_code="000001.OF"):

        data = self.get_fund_holding_all()
        data_date = data[data['FundCode'] == fund_code]
        data_date = data_date.reset_index(drop=True)
        return data_date

    def get_fund_holding_report_date_fund(self, fund_code="000001.OF", report_date=None):

        if report_date is None:
            date_series = Date().get_normal_date_series(beg_date=None, end_date=datetime.today(), period='Q')
            report_date = date_series[-2]

        data = self.get_fund_holding_all()
        data = data[data['FundCode'] == fund_code]
        data = data[data['Date'] == report_date]
        data.index = data.StockCode
        data = data.sort_values(by=['Weight'], ascending=False)
        fund_holding = data[~data.index.duplicated()]
        return fund_holding

if __name__ == '__main__':

    # FundHolder().load_fund_holding("19991231", datetime.today())
    print(FundHolder().get_fund_holding_report_date())
    print(FundHolder().get_fund_holding_report_date_fund())


