import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta
from quant.mfc.mfc_data import MfcData
from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.utility_fun.code_format import get_stcok_market, stock_code_add_postfix
from quant.data_source.my_ftp import MyFtp
import warnings
from WindPy import w
w.start()

"""
每天开盘后10点计算 新股当天有没有开板 若开板 则卖出 生成恒生交易单
交易量>0 并且 收益率<9% 则视为开板
"""


def cal_ipo_sell():

    out_path = 'E:\\3_Data\\7_other_data\\4_cal_ipo_sell\\'
    new_days = 60

    today = datetime.today().strftime("%Y%m%d")

    Date().load_trade_date_series("D")
    # MfcData().load_ftp_daily(date=today)
    # MfcData().change_ftp_file(date=today)

    before_trade_data = Date().get_trade_date_offset(today, -1)

    data = MfcData().get_fund_security(before_trade_data)
    data = data.dropna(subset=['基金名称'])
    data = data[['基金名称', '证券代码', '持仓', '证券类别']]
    data.columns = ['FundName', 'StockCode', 'Holding', 'Type']
    data = data[data.Type == '股票']
    data.StockCode = data.StockCode.map(stock_code_add_postfix)
    data["Market"] = data.StockCode.map(get_stcok_market)

    Stock().load_all_stock_code_now()
    Stock().load_ipo_date()
    stock = Stock().get_ipo_date()
    stock.columns = ['IpoDate', 'DelistDate']
    stock['StockCode'] = stock.index
    stock['IpoDate'] = stock['IpoDate'].map(lambda x: str(int(x)))

    new_stock_date = datetime.today() - timedelta(days=new_days)
    new_stock_date = new_stock_date.strftime("%Y%m%d")

    all_data = pd.merge(data, stock, on=['StockCode'], how="left")
    all_data = all_data[all_data.IpoDate > new_stock_date]

    code_list = list(set(all_data.StockCode.values))
    code_str = ','.join(code_list)
    pct = w.wsq(code_str, "rt_pct_chg,rt_vol")
    pct = pd.DataFrame(pct.Data, columns=pct.Codes, index=['Pct', 'Vol']).T
    pct['StockCode'] = pct.index

    new_data = pd.merge(all_data, pct, on=['StockCode'], how="left")
    new_data = new_data[new_data['Vol'] > 0]
    new_data = new_data[new_data['Pct'] < 0.09]

    fund_list = list(set(data['FundName']))

    for i_fund in range(len(fund_list)):

        fund_name = fund_list[i_fund]
        fund_data = new_data[new_data.FundName == fund_name]
        out_sub_path = os.path.join(out_path, today)
        if not os.path.exists(out_sub_path):
            os.mkdir(out_sub_path)
            print(" Make Folder At ", today)

        if len(fund_data) > 0:

            warnings.filterwarnings("ignore")
            fund_data_out = fund_data[['StockCode', 'Holding', 'Market']]
            fund_data_out.columns = ['Ticker', 'Shares', 'Market']
            fund_data_out['Direction'] = 2
            fund_data_out['Price'] = 0
            fund_data_out['Market Code'] = fund_data_out['Market'].map(lambda x: 1 if x == 'SH' else 2)
            fund_data_out['Price Model'] = 4
            fund_data_out['Ticker'] = fund_data_out['Ticker'].map(lambda x: x[0:6])

            fund_data_out = fund_data_out[['Ticker', 'Direction', 'Shares', 'Price', 'Price Model', 'Market Code']]

            file = fund_name + '.xls'
            out_file = os.path.join(out_sub_path, file)
            print(out_file)
            fund_data_out.to_excel(out_file, index=None)
            ftp = MyFtp()
            ftp.connect()
            ftp_file = os.path.join("\\ipo_stock\\", today, file)
            ftp.upload_file(ftp_file, out_file)
            ftp.close()


if __name__ == '__main__':

    cal_ipo_sell()
