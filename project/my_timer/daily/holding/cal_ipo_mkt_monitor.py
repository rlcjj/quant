import numpy as np
import pandas as pd
import os
from datetime import datetime
from quant.mfc.mfc_data import MfcData
from quant.stock.date import Date
from quant.utility_fun.code_format import get_stcok_market, stock_code_add_postfix

"""
每天开盘前计算 前20个交易日 各个公募基金两市分别的股票市值
现在打新的下限 是在某个市场上 股票市值20个交易日的平均值 大于6000万
计算前20个交易日基金股票市值的平均值 利用20*6000万-前19个交易日的股票市值=昨天能够打新的市值下限
这样计算出的结果和昨天真实持仓的差就是 今天应该增加多少股票市值
所需要的文件是所有基金的证券持仓 和 当日的收盘价
"""


def cal_ipo_mkt_monitor(today, project_path, out_path):

    # 参数
    ###########################################################################
    thread_value = 60000000
    day_period = 20
    person_list = ['liuxin', 'yangchao', 'liuyang']

    before_trade_data = Date().get_trade_date_offset(today, -1)
    trade_series = Date().get_trade_date_series(end_date=before_trade_data)
    trade_series = pd.DataFrame(trade_series, index=trade_series)
    trade_series = list(trade_series.index[-day_period:])

    # 基金经理管理的基金
    ###########################################################################
    fund = pd.read_excel(project_path + 'Manage_Fund_Name.xlsx', encoding='gbk')

    # 所需要的持仓文件
    #######################################################################################################
    holding_data = pd.DataFrame([])
    for i_date in range(len(trade_series)):

        date = trade_series[i_date]
        data = MfcData().get_group_security(date)
        data = data.dropna(subset=['基金名称'])

        data = data[['基金名称', '证券代码', '持仓', '证券类别', '最新价']]
        data.columns = ['FundName', 'StockCode', 'Holding', 'Type', 'Price']
        data['Date'] = date
        data = data[data.Type == '股票']
        data.StockCode = data.StockCode.map(stock_code_add_postfix)
        data["Market"] = data.StockCode.map(get_stcok_market)
        data['Holding'] = data['Holding'].astype(np.float)
        data['Price'] = data['Price'].astype(np.float)
        data['StockMarketValue'] = data['Holding'] * data['Price']
        holding_data = pd.concat([holding_data, data], axis=0)

    holding_data = holding_data.reset_index(drop=True)

    # 开始计算每只基金的股票平均市值
    #######################################################################################################
    for i_col in range(len(person_list)):

        person_name = person_list[i_col]
        fund_val = fund.ix[:, person_name]
        fund_val = fund_val.dropna()
        fund_list = list(fund_val.values)

        columns = ['沪市平均', '沪市最新', '沪市目标', '深市平均', '深市最新', '深市目标']
        result = pd.DataFrame([], index=fund_list, columns=columns)

        for i_fund in range(len(fund_list)):

            fund_name = fund_list[i_fund]
            print(" Cal Fund IPO Stock MarketValue 20 days ", fund_name)

            holding_data_fund = holding_data[holding_data.FundName == fund_name]
            fund_gb = holding_data_fund.groupby(by=['Date', 'Market'])['StockMarketValue'].sum()
            fund_gb = fund_gb.unstack()

            result.ix[fund_name, "沪市平均"] = fund_gb.ix[:, "SH"].mean()
            result.ix[fund_name, "沪市最新"] = fund_gb.ix[-1, "SH"]
            result.ix[fund_name, "沪市目标"] = thread_value * day_period - fund_gb.ix[0:-1, "SH"].sum()
            result.ix[fund_name, "深市平均"] = fund_gb.ix[:, "SZ"].mean()
            result.ix[fund_name, "深市最新"] = fund_gb.ix[-1, "SZ"]
            result.ix[fund_name, "深市目标"] = thread_value * day_period - fund_gb.ix[0:-1, "SZ"].sum()

        result = result[(result["沪市平均"] < thread_value) | (result["深市平均"] < thread_value)]
        result /= 10000

        out_sub_path = os.path.join(out_path, person_name, today, 'ipo_mkt_monitor')
        if not os.path.exists(out_sub_path):
            os.makedirs(out_sub_path)
        out_file = os.path.join(out_sub_path, '新股市值监控.csv')
        result.to_csv(out_file)

if __name__ == '__main__':

    project_path = 'D:\\Program Files (x86)\\anaconda\\Lib\\site-packages\\quant\\project\\my_timer\\input_data\\'
    out_path = 'E:\\3_数据\\7_other_data\\0_mail_holding_all\\'
    today = datetime.today().strftime("%Y%m%d")
    today = datetime(2018, 7, 6).strftime("%Y%m%d")
    cal_ipo_mkt_monitor(today, project_path, out_path)
