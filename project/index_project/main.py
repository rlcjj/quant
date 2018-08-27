import pandas as pd
from datetime import datetime
from quant.stock.index import Index
from quant.stock.date import Date
from quant.utility_fun.write_pandas_to_excel import write_pandas
import numpy as np


def index_position(index_code, fixed_pct_yearly, target_nav, init_date, end_date):

    # 参数
    ####################################################################################################
    # index_code = '000905.SH'
    # fixed_pct_yearly = 0.03
    # init_date = datetime(2013, 1, 1)
    # end_date = datetime(2014, 6, 29)
    # target_nav = 1.06

    init_nav = 1.00

    init_target_pct = (target_nav / init_nav) - 1.0

    expect_roe = 0.10
    year_days = 250
    max_stock_position = 0.80
    max_expect_port_pct = 0.25
    max_stock_pct = 0.30
    min_stock_position = 0.00

    # 计算
    ####################################################################################################

    # # 得到数据
    init_date = Date().get_trade_date_offset(init_date, -1)
    index_pct = Index(index_code).get_index_pct_period(init_date, end_date)
    pb = Index(index_code).get_index_attr_period(init_date, end_date, "PB_LF")
    data = pd.concat([index_pct, pb], axis=1)
    data.index.name = 'Date_Int'
    data.columns = ['Index_Pct', 'PB_LF']
    data['Cum_Index_Pct'] = (data['Index_Pct'] + 1).cumprod() - 1.0

    # init_pe = data.ix[0, "PE_TTM"]
    # 历史平均值
    trade_days = len(data)

    before_date = Date().get_trade_date_offset(init_date, -trade_days)
    pb = Index(index_code).get_index_attr_period(before_date, init_date, "PB_LF")
    init_pe = pb.median()
    init_pe = data.ix[0, 'PB_LF']
    expect_pe_change = init_pe / data.ix[0, 'PB_LF']

    init_expect_stock_pct = expect_roe * trade_days / year_days + expect_pe_change - 1.0
    fixed_pct = fixed_pct_yearly * trade_days / year_days

    # # 预期净值 预期股票收益 预期固定收益
    data['Date_Number'] = range(1, trade_days + 1)
    data['Remain_Days'] = trade_days - data["Date_Number"]
    data['Cur_Target_Nav'] = target_nav / (1 + (data["Remain_Days"] / year_days) * fixed_pct_yearly)

    data['ROE'] = expect_roe
    data['Stock_Expected_ROE_Return'] = data.ROE * data.Remain_Days / year_days
    data['Init_Expected_PB'] = expect_pe_change * init_pe
    data['Cur_Expected_PB'] = (data.Init_Expected_PB * data.Remain_Days + data.PB_LF * data.Date_Number) / trade_days
    data['Stock_Expected_PB_Return'] = data.Cur_Expected_PB / data.PB_LF - 1.0
    data['Stock_Expected_Return'] = (data['Stock_Expected_ROE_Return'] + 1.0) * (data['Stock_Expected_PB_Return'] + 1.0) - 1
    data['Stock_Expected_Return'] = data['Stock_Expected_Return'].map(lambda x: min(x, max_stock_pct))

    data['Fixed_Expected_Return'] = fixed_pct * data.Remain_Days / trade_days
    data['Fixed_Pct'] = fixed_pct / trade_days
    res = pd.DataFrame([], columns=['finish_nav'])
    res.ix[init_date, 'end_date'] = end_date
    flag = None
    number = 0
    data['Exp_Stock_Position'] = np.nan

    # # 每天计算
    for i_date in range(len(data)):

        if i_date == 0:

            cur_date = data.index[i_date]
            print(" Init ", cur_date)
            init_stock_position = (init_target_pct - fixed_pct) / (init_expect_stock_pct - fixed_pct)
            init_stock_position = min(init_stock_position, max_stock_position)
            data.ix[i_date, 'Cur_Close_Stock_Position'] = init_stock_position
            data.ix[i_date, 'Cur_Close_Fixed_Position'] = 1.0 - init_stock_position
            data.ix[i_date, "Portfolio_Nav"] = init_nav
            data.ix[i_date, "Portfolio_Pct"] = 0.0
            data.ix[i_date, "Change"] = "Change"
            number += 1

        else:

            cur_date = data.index[i_date]
            before_nav = data.ix[i_date - 1, "Portfolio_Nav"]
            cur_target_nav = data.ix[i_date, "Cur_Target_Nav"]

            before_stock_position = data.ix[i_date - 1, 'Cur_Close_Stock_Position']
            before_fixed_position = data.ix[i_date - 1, 'Cur_Close_Fixed_Position']

            today_stock_pct = data.ix[i_date, 'Index_Pct']
            today_fixed_pct = data.ix[i_date, 'Fixed_Pct']

            today_stock_nav = before_stock_position * (today_stock_pct + 1.0)
            today_fixed_nav = before_fixed_position * (today_fixed_pct + 1.0)

            cur_stock_position = today_stock_nav / (today_stock_nav + today_fixed_nav)
            cur_fixed_position = today_fixed_nav / (today_stock_nav + today_fixed_nav)

            cur_port_pct = today_stock_pct * before_stock_position + today_fixed_pct * before_fixed_position
            cur_port_nav = before_nav * (1 + cur_port_pct)

            data.ix[i_date, 'Cur_Close_Stock_Position'] = cur_stock_position
            data.ix[i_date, 'Cur_Close_Fixed_Position'] = cur_fixed_position
            data.ix[i_date, "Portfolio_Pct"] = cur_port_pct
            data.ix[i_date, "Portfolio_Nav"] = cur_port_nav

            if cur_port_nav >= cur_target_nav:

                print(" Target Finish ", cur_date)
                data.ix[i_date, "Cur_Close_Stock_Position"] = 0.0
                data.ix[i_date, "Cur_Close_Fixed_Position"] = 1.0

                if flag is None:

                    res.ix[init_date, 'finish_date'] = cur_date
                    data.ix[i_date, "Change"] = "Change"
                    number += 1
                    flag = 'f'

            else:
                # remain_days = data.ix[i_date, "Remain_Days"]
                # remain_ratio = remain_days / trade_days
                # expect_port_pct = (target_nav * remain_ratio + cur_port_nav * (1- remain_ratio)) / cur_port_nav - 1.0
                expect_port_pct = target_nav / cur_port_nav - 1.0
                expect_port_pct = min(expect_port_pct, max_expect_port_pct)
                data.ix[i_date, 'Exp_Portfolio_Pct'] = expect_port_pct
                expect_stock_pct = data.ix[i_date, 'Stock_Expected_Return']
                expect_fixed_pct = data.ix[i_date, 'Fixed_Expected_Return']
                if (expect_port_pct > expect_fixed_pct) and (expect_port_pct < expect_stock_pct):
                    expect_stock_position = (expect_port_pct - expect_fixed_pct) / (expect_stock_pct - expect_fixed_pct)
                    expect_stock_position = np.min([expect_stock_position, max_stock_position])
                    expect_stock_position = np.max([expect_stock_position, min_stock_position])
                elif expect_stock_pct < expect_fixed_pct:
                    data.ix[i_date, "Cur_Close_Stock_Position"] = 0.0
                    data.ix[i_date, "Cur_Close_Fixed_Position"] = 1.0
                    expect_stock_position = 0.0
                else:
                    expect_stock_position = cur_stock_position
                # expect_stock_position = cur_stock_position
                stock_diff = np.abs(cur_stock_position - expect_stock_position)
                data.ix[i_date, 'Exp_Stock_Position'] = expect_stock_position

                if stock_diff > 0.04:

                    diff = expect_stock_position - cur_stock_position
                    print(" %s Postion Change %.2f%% Now %.2f%% " % (cur_date, diff*100, expect_stock_position*100))
                    data.ix[i_date, "Cur_Close_Stock_Position"] = expect_stock_position
                    data.ix[i_date, "Cur_Close_Fixed_Position"] = 1.0 - expect_stock_position
                    data.ix[i_date, "Change"] = "Change"
                    number += 1

    data["Change_Position"] = data['Cur_Close_Stock_Position'].diff()
    res.ix[init_date, "stock_position"] = data["Cur_Close_Stock_Position"].mean()
    res.ix[init_date, "finish_nav"] = data['Portfolio_Nav'].values[-1]
    res.ix[init_date, "target_nav"] = target_nav
    res.ix[init_date, "finish_if"] = res.ix[init_date, "finish_nav"] >= res.ix[init_date, "target_nav"]
    res.ix[init_date, "number"] = number

    data_drop = data.dropna(subset=['Exp_Stock_Position'])
    if len(data_drop) > 0:
        res.ix[init_date, 'index_cum_pct'] = data_drop['Cum_Index_Pct'].values[-1]

    # 写入
    ####################################################################################################
    num_format_pd = pd.DataFrame([], columns=data.columns, index=['format'])
    num_format_pd.ix['format', :] = '0.00%'
    num_format_pd.ix['format', ['PB_LF', 'Date_Number', 'Remain_Days',
                                'Init_Expected_PB', 'Cur_Expected_PB',
                                'Portfolio_Nav', 'Cur_Target_Nav']] = '0.00'

    save_path = 'C:\\Users\\doufucheng\\OneDrive\\Desktop\\data\\'
    begin_row_number = 0
    begin_col_number = 1
    color = "red"
    file_name = save_path + index_code + '_' + init_date + '_' + end_date + ".xlsx"
    sheet_name = "指数测试"

    write_pandas(file_name, sheet_name, begin_row_number, begin_col_number, data, num_format_pd, color)
    print(res)
    return res
    ####################################################################################################


def test_all():

    index_code = '000016.SH'
    fixed_pct_yearly = 0.04
    target_nav = 1.08

    date_data = Date().get_trade_date_series("20071231", datetime.today(), "M")

    for i in range(len(date_data)-12):
        init_date = date_data.index[i]
        end_date = date_data.index[i+12]
        print(init_date, end_date)
        res = index_position(index_code, fixed_pct_yearly, target_nav, init_date, end_date)
        if i == 0:
            result = res
        else:
            result = pd.concat([result, res], axis=0)

    ############################################################################################
    num_format_pd = pd.DataFrame([], columns=result.columns, index=['format'])
    num_format_pd.ix['format', :] = '0.00'

    save_path = 'C:\\Users\\doufucheng\\OneDrive\\Desktop\\data\\'
    begin_row_number = 0
    begin_col_number = 1
    color = "red"
    file_name = save_path + index_code + ".xlsx"
    sheet_name = "指数测试"

    result.to_csv(save_path + index_code + ".csv")
    write_pandas(file_name, sheet_name, begin_row_number, begin_col_number, result, num_format_pd, color)
    print(result)

if __name__ == '__main__':

    index_code = '000905.SH'
    fixed_pct_yearly = 0.04
    target_nav = 1.08
    init_date, end_date = '20140101', '20141231'
    index_position(index_code, fixed_pct_yearly, target_nav, init_date, end_date)

    test_all()

