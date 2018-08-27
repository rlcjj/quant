import numpy as np
import pandas as pd
import os
from datetime import datetime
from quant.mfc.mfc_data import MfcData
from quant.stock.date import Date
from quant.utility_fun.code_format import  stock_code_add_postfix

"""
每天开盘前计算 前5个交易日 各个基金的股票成交情况
不能自反向 ：若每只基金自身 前五天有卖出（买入）情况某只股票的情况 那么基金当天不能买入（卖出）
"""


def cal_reverse_5days(today, project_path, out_path):

    # 参数
    ###########################################################################
    person_list = ['liuxin', 'yangchao', 'caolongjie', 'liuyang']
    day_period = 5

    # 日期参数
    ###########################################################################
    before_trade_data = Date().get_trade_date_offset(today, -1)
    trade_series = Date().get_trade_date_series(end_date=before_trade_data)
    trade_series = pd.DataFrame(trade_series, index=trade_series)
    trade_series = list(trade_series.index[-day_period:])

    # 基金经理管理的基金
    ###########################################################################
    fund = pd.read_excel(project_path + 'Manage_Fund_Name.xlsx', encoding='gbk')
    result = pd.DataFrame([])

    # 开始计算每只基金的5日五日反向
    #######################################################################################################
    for i_col in range(len(person_list)):

        person_name = person_list[i_col]
        fund_val = fund.ix[:, person_name]
        fund_val = fund_val.dropna()
        fund_list = list(fund_val.values)

        for i_fund in range(len(fund_list)):

            fund_name = fund_list[i_fund]
            print(" Cal Fund Reverse 5 days ", fund_name)

            for i_date in range(len(trade_series)):

                cur_date = trade_series[i_date]
                data = MfcData().get_trade_statement(cur_date)
                data = data.dropna(subset=['基金名称'])
                data = data[['基金名称', '证券代码', '委托方向', '成交数量', '资产类别']]
                data.columns = ['FundName', 'StockCode', 'Direction', 'TradeNumber', 'Type']
                data = data[data.FundName == fund_name]
                data = data[data.Type == '股票资产']
                data.StockCode = data.StockCode.map(stock_code_add_postfix)
                data.Direction = data.Direction.map(lambda x: 2 if x == '卖出' else 1)

                result_date = pd.DataFrame(data.Direction.values, index=data.StockCode.values, columns=[cur_date])
                if i_date == 0:
                    result = result_date
                else:
                    try:
                        result = pd.concat([result, result_date], axis=1)
                    except:
                        pass

            result = result.fillna(0)
            result.index.name = 'CODE'
            result = result.astype(np.int)

            my_result = []

            for i_row in range(len(result)):

                vals_list = list(result.ix[i_row, trade_series])
                vals_set = list(set(result.ix[i_row, trade_series]))

                if 2 in vals_set:
                    append_row = [result.index[i_row], 2]
                    append_row.extend(vals_list)
                    my_result.append(append_row)

                if 1 in vals_set:
                    append_row = [result.index[i_row], 1]
                    append_row.extend(vals_list)
                    my_result.append(append_row)

            col = ['CODE', 'FLAG']
            col.extend(trade_series)
            my_result = pd.DataFrame(my_result, columns=col)

            out_sub_path = os.path.join(out_path, person_name, today, 'reverse_5days')
            if not os.path.exists(out_sub_path):
                os.makedirs(out_sub_path)
            out_file = os.path.join(out_sub_path, fund_name + '.csv')
            my_result.to_csv(out_file, index=None)
            print(fund_name, len(result), len(my_result))
    #######################################################################################################

if __name__ == '__main__':

    project_path = 'D:\\Program Files (x86)\\anaconda\\Lib\\site-packages\\quant\\project\\my_timer\\input_data\\'
    out_path = 'E:\\3_数据\\7_other_data\\0_mail_holding_all\\'
    today = datetime.today().strftime("%Y%m%d")
    today = datetime(2018, 6, 27).strftime("%Y%m%d")
    cal_reverse_5days(today, project_path, out_path)
