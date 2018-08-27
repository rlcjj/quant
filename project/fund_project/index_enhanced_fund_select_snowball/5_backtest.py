import pandas as pd
import numpy as np
from datetime import datetime
from quant.utility_fun.write_pandas_to_excel import write_pandas
from quant.stock.date import Date
from quant.fund.fund import Fund
from quant.stock.index import Index
from WindPy import w
w.start()


def backtest(index_name, now_date, path):

    # 参数
    ##################################################################################################################
    # index_name = '中证500'
    # now_date = "20180715"
    # path = 'E:\\3_数据\\4_fund_data\\6_index_enhanced_fund_snowball\\'

    # 日期
    ##################################################################################################################
    date_series = Date().get_normal_date_series("20130622", datetime.today(), period="S")
    # date_series.remove("20180630")
    date_series.append(now_date)

    # 循环取出持仓基金
    ##################################################################################################################
    out_path = path + 'score_fund\\' + index_name + '\\'

    holding_fund_total = pd.DataFrame([])
    holding_fund_pct = pd.DataFrame([], index=date_series, columns=['下期超额收益'])

    for i_date in range(0, len(date_series)):

        report_date = date_series[i_date]
        print(report_date)
        filename = out_path + '基金得分_' + index_name + '_' + report_date + '.xlsx'
        fund_score = pd.read_excel(filename, index_col=[0], encoding='gbk')
        fund_score = fund_score[['基金名称', '下期超额收益', '总得分',
                                 '跟踪误差得分', '超额收益得分', '信息比率得分', '风格暴露得分', '上期超额收益']]
        fund_score['基金公司'] = fund_score['基金名称'].map(lambda x: x[0:2])
        fund_score['基金代码'] = fund_score.index
        fund_score_drop = fund_score.groupby(['基金公司']).apply(lambda i: i.iloc[0, :] if len(i) >= 1 else np.nan)
        fund_score_drop = fund_score_drop.sort_values(by=['总得分'], ascending=False)

        fund_score_drop_0 = fund_score_drop[fund_score_drop['上期超额收益'] > 0.0]
        if len(fund_score_drop_0) >= 5:
            fund_score_drop = fund_score_drop_0

        fund_score_five = fund_score_drop.iloc[0:min(5, len(fund_score)), :]
        if len(fund_score_five) > 0.0:
            fund_score_five['权重'] = 1.0 / len(fund_score_five)
            fund_score_five['换仓日期'] = report_date
            holding_fund_total = pd.concat([holding_fund_total, fund_score_five], axis=0)
            pct = (fund_score_five['权重'] * fund_score_five['下期超额收益']).sum()
            holding_fund_pct.ix[report_date, "下期超额收益"] = pct

    # 循环取出持仓基金
    ##################################################################################################################
    num_format_pd = pd.DataFrame([], columns=holding_fund_total.columns, index=['format'])
    num_format_pd.ix['format', :] = '0.00'
    num_format_pd.ix['format', ['下期超额收益', '上期超额收益']] = '0.00%'
    begin_row_number = 0
    begin_col_number = 0
    color = "red"
    file_name = path + 'select_fund\\' + index_name + '\\' + '基金每期持仓_' + index_name + '.xlsx'
    sheet_name = "基金每期持仓"
    write_pandas(file_name, sheet_name, begin_row_number, begin_col_number, holding_fund_total, num_format_pd, color)

    num_format_pd = pd.DataFrame([], columns=holding_fund_pct.columns, index=['format'])
    num_format_pd.ix['format', :] = '0.00'
    num_format_pd.ix['format', '下期超额收益'] = '0.00%'
    begin_row_number = 0
    begin_col_number = 0
    color = "red"
    file_name = path + 'select_fund\\' + index_name + '\\' + '基金每期超额收益_' + index_name + '.xlsx'
    sheet_name = "基金每期超额收益"
    write_pandas(file_name, sheet_name, begin_row_number, begin_col_number, holding_fund_pct, num_format_pd, color)


def nav(index_code, index_name, now_date):

    # 参数
    ##################################################################################################################
    # index_name = '中证500'
    # index_code = '000905.SH'
    # now_date = "20180715"

    # 日期
    ##################################################################################################################
    date_series = Date().get_normal_date_series("20130622", datetime.today(), period="S")
    date_series.append(now_date)

    # 循环计算基金净值
    ##################################################################################################################
    path = 'E:\\4_代码\\pycharmprojects\\31_雪球优选增强基金\\output_data\\'
    file_name = path + 'select_fund\\' + index_name + '\\' + '基金每期持仓_' + index_name + '.xlsx'
    fund_holding_total = pd.read_excel(file_name, index_col=[0], encoding='gbk')
    fund_holding_total['换仓日期'] = fund_holding_total['换仓日期'].map(str)

    nav_total = pd.DataFrame([])

    for i_date in range(0, len(date_series)-2):

        report_date_str = date_series[i_date]
        report_date_str_after = date_series[i_date + 1]
        print(report_date_str, report_date_str_after)

        fund_holding_date = fund_holding_total[fund_holding_total['换仓日期'] == report_date_str]

        fund_code_list = list(fund_holding_date['基金代码'].values)
        fund_data = Fund().get_fund_factor("Repair_Nav", None, None)
        fund_data = fund_data.ix[report_date_str: report_date_str_after, fund_code_list]
        fund_data = fund_data / fund_data.iloc[0, :]
        fund_data = fund_data.dropna()
        nav_array = fund_data.values
        weight_array = np.row_stack(fund_holding_date.ix[:, '权重'].values)

        fund_data.loc[:, '每日总资产'] = np.dot(nav_array, weight_array)
        fund_data['每日涨跌幅'] = fund_data['每日总资产'].pct_change()
        fund_data = fund_data.dropna()
        nav_total = pd.concat([nav_total, fund_data['每日涨跌幅']], axis=0)

    nav_total = nav_total[~nav_total.index.duplicated()]
    index_pct = Index().get_index_factor(index_code, None, None, ["PCT"])
    result = pd.concat([nav_total, index_pct], axis=1)
    result = result.dropna()
    result.columns = ['基金组合日涨跌', '指数日涨跌']
    result['基金组合累计收益'] = (result['基金组合日涨跌'] + 1).cumprod() - 1
    result['指数累计收益'] = (result['指数日涨跌'] + 1).cumprod() - 1
    result['超额累计收益'] = result['基金组合累计收益'] - result['指数累计收益']

    num_format_pd = pd.DataFrame([], columns=result.columns, index=['format'])
    num_format_pd.ix['format', :] = '0.00%'
    begin_row_number = 0
    begin_col_number = 0
    color = "red"
    file_name = path + 'nav\\' + index_name + '\\' + '基金回测净值_' + index_name + '.xlsx'
    sheet_name = "基金回测净值"
    write_pandas(file_name, sheet_name, begin_row_number, begin_col_number, result, num_format_pd, color)


if __name__ == '__main__':

    now_date = "20180715"
    path = 'E:\\3_数据\\4_fund_data\\6_index_enhanced_fund_snowball\\'

    # 回测
    ###################################################################
    index_name = '中证500'
    backtest(index_name, now_date, path)

    index_name = '沪深300'
    backtest(index_name, now_date, path)

    # 计算净值
    ##################################################################
    index_name = '中证500'
    index_code = '000905.SH'
    nav(index_code, index_name, now_date)

    index_name = '沪深300'
    index_code = '000300.SH'
    nav(index_code, index_name, now_date)

