import pandas as pd
from WindPy import w
w.start()
from datetime import datetime
import numpy as np
from quant.utility_fun.write_pandas_to_excel import write_pandas
from quant.fund.fund import Fund
from quant.stock.index import Index
from quant.stock.date import Date
import os


def calculate_fund_factor_date(date, index_code, index_name, out_path):

    # 参数
    ########################################################################################################

    # index_code = '000905.SH'
    # index_name = '中证500'
    # date = '2015-12-31'
    # min_period = 200
    # out_path = 'E:\\4_代码\\pycharmprojects\\31_雪球优选增强基金\\output_data\\cal_fund_factor\\zz500\\'

    # 日期数据
    ########################################################################################################
    min_period = 200
    date_cur = datetime.strptime(date, "%Y%m%d")
    date_cur_int = date_cur.strftime('%Y%m%d')
    date_bef_1y = datetime(year=date_cur.year-1, month=date_cur.month, day=date_cur.day).strftime("%Y-%m-%d")
    date_aft_hy = (date_cur + pd.tseries.offsets.DateOffset(months=6, days=0)).strftime("%Y-%m-%d")

    # 读取数据 基金池 基金净值数据 指数收盘价数据
    ########################################################################################################

    path = os.path.join(out_path, 'filter_fund_pool\\')
    file = os.path.join(path, '基金最终筛选池_' + index_name + '.xlsx')
    fund_code = pd.read_excel(file, index_col=[1], encoding='gbk')

    fund_nav = Fund().get_fund_factor("Repair_Nav")
    index_close = Index().get_index_factor(index_code, None, None, attr=['CLOSE'])
    index_close.columns = [index_code]

    # 筛选新基金 并下载基金规模
    #######################################################################################################

    fund_code = fund_code.ix[:, ['上市日期', '基金简称']]
    fund_code = fund_code[fund_code['上市日期'] < date_bef_1y]

    fund_code_str = ','.join(fund_code.index)
    fund_asset = w.wss(fund_code_str, "netasset_total", "unit=1;tradeDate=" + str(date))
    fund_asset = pd.DataFrame(fund_asset.Data, index=['基金规模'], columns=fund_asset.Codes).T
    fund_asset['基金规模'] /= 100000000.0
    fund_asset['基金规模'] = fund_asset['基金规模'].round(2)
    fund_asset = fund_asset[fund_asset['基金规模'] > 0.5]
    fund_info = pd.concat([fund_code, fund_asset], axis=1)
    fund_info = fund_info.dropna()

    # 计算最近1年 各项指标
    ########################################################################################################
    result = pd.DataFrame([], index=fund_code.index, columns=['最近1年跟踪误差'])
    fund_nav = fund_nav.ix[index_close.index, fund_code.index]
    fund_pct = fund_nav.pct_change()
    index_pct = index_close.pct_change()
    index_pct = index_pct[index_code]
    fund_excess_pct = fund_pct.sub(index_pct, axis='index')
    fund_excess_pct_period = fund_excess_pct.ix[date_bef_1y:date, :]
    fund_nav_period = fund_nav.ix[date_bef_1y:date, :]
    index_close_prioed = index_close.ix[date_bef_1y:date, :]
    result.ix[:, "最近1年数据长度"] = fund_excess_pct_period.count()
    result.ix[:, "最近1年跟踪误差"] = fund_excess_pct_period.std() * np.sqrt(250)
    # last_date_nav = fund_nav_period.iloc[len(fund_nav_period)-1, :]
    # first_date_nav = fund_nav_period.iloc[0, :]
    fund_return_log =(fund_nav_period.pct_change()+1.0).applymap(np.log).cumsum().ix[-1,:]
    fund_return = fund_return_log.map(np.exp) - 1
    last_date_close = index_close_prioed.iloc[len(fund_nav_period)-1, :]
    first_date_close = index_close_prioed.iloc[0, :]
    result.ix[:, "最近1年基金涨跌"] = fund_return
    result.ix[:, "最近1年指数涨跌"] = (last_date_close / first_date_close - 1.0).values[0]
    result.ix[:, "最近1年超额收益"] = result.ix[:, "最近1年基金涨跌"] - result.ix[:, "最近1年指数涨跌"]
    result.ix[:, "最近1年信息比率"] = result.ix[:, "最近1年超额收益"] / result.ix[:, "最近1年跟踪误差"]

    result = result[result['最近1年数据长度'] > min_period]

    # 计算之后半年 各项指标
    ########################################################################################################
    fund_excess_pct_period = fund_excess_pct.ix[date:date_aft_hy, :]
    fund_nav_period = fund_nav.ix[date:date_aft_hy, :]
    index_close_prioed = index_close.ix[date:date_aft_hy, :]
    result.ix[:, "之后半年数据长度"] = fund_excess_pct_period.count()
    result.ix[:, "之后半年跟踪误差"] = fund_excess_pct_period.std() * np.sqrt(250)
    try:
        fund_return_log = (fund_nav_period.pct_change() + 1.0).applymap(np.log).cumsum().ix[-1, :]
        fund_return = fund_return_log.map(np.exp) - 1
        result.ix[:, "之后半年基金涨跌"] = fund_return
    except:
        result.ix[:, "之后半年基金涨跌"] = np.nan

    try:
        last_date_close = index_close_prioed.iloc[len(fund_nav_period) - 1, :]
        first_date_close = index_close_prioed.iloc[0, :]
        result.ix[:, "之后半年指数涨跌"] = (last_date_close / first_date_close - 1.0).values[0]
    except:
        result.ix[:, "之后半年指数涨跌"] = np.nan

    result.ix[:, "之后半年超额收益"] = result.ix[:, "之后半年基金涨跌"] - result.ix[:, "之后半年指数涨跌"]
    result.ix[:, "之后半年信息比率"] = result.ix[:, "之后半年超额收益"] / result.ix[:, "之后半年跟踪误差"]

    result = pd.concat([fund_info, result], axis=1)
    result = result.dropna(subset=["基金规模"])
    result = result.fillna("")

    # 写到EXCEL表
    ################################################################################################
    out_path = os.path.join(out_path, "cal_fund_factor\\" + index_name)

    num_format_pd = pd.DataFrame([], columns=result.columns, index=['format'])
    num_format_pd.ix['format', :] = '0.00%'
    num_format_pd.ix['format', '之后半年数据长度'] = '0.00'
    num_format_pd.ix['format', '之后半年信息比率'] = '0.00'
    num_format_pd.ix['format', '基金规模'] = '0.00'
    num_format_pd.ix['format', '最近1年信息比率'] = '0.00'
    num_format_pd.ix['format', '最近1年数据长度'] = '0.00'

    begin_row_number = 0
    begin_col_number = 0
    color = "red"
    file_name = os.path.join(out_path, '基金指标_' + index_name + '_' + date_cur_int + '.xlsx')
    sheet_name = "基金指标"
    write_pandas(file_name, sheet_name, begin_row_number, begin_col_number, result, num_format_pd, color)
    ################################################################################################################

    return True


def calculate_fund_factor(now_date, out_path):

    # 半年计算一次
    ################################################################################################################
    # now_date = "20180715"
    # out_path = 'E:\\3_数据\\4_fund_data\\6_index_enhanced_fund_snowball\\'

    data = Date().get_normal_date_series("20130622", datetime.today(), period="S")
    data.append(now_date)

    # 中证500
    ################################################################################################################
    index_code = '000905.SH'
    index_name = '中证500'

    for i_date in range(10, len(data)):

        report_date = data[i_date]
        print("正在计算基金指标 %s %s" % (index_name, report_date))
        calculate_fund_factor_date(report_date, index_code, index_name, out_path)

    # 沪深300
    ################################################################################################################
    index_code = '000300.SH'
    index_name = '沪深300'

    for i_date in range(10, len(data)):

        report_date = data[i_date]
        print("正在计算基金指标 %s %s" % (index_name, report_date))
        calculate_fund_factor_date(report_date, index_code, index_name, out_path)

    ###############################################################################################################


if __name__ == '__main__':

    now_date = "20180815"
    out_path = 'E:\\3_Data\\4_fund_data\\6_index_enhanced_fund_snowball\\'
    calculate_fund_factor(now_date, out_path)
