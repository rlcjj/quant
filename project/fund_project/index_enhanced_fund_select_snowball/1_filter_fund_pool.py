import pandas as pd
import numpy as np
import os
from quant.utility_fun.write_pandas_to_excel import write_pandas
from quant.fund.fund import Fund
from quant.stock.index import Index
from WindPy import w
w.start()


def filter_fund_pool(index_code, begin_date, end_date,
                     min_period, ipo_date, track_error_up,
                     index_name, out_path):

    #############################################################################################
    # begin_date = '2017-05-31'
    # end_date = '2018-05-31'
    # ipo_date = '2017-05-31'
    # min_period = 200
    # index_name = '沪深300'
    # index_code = '000300.SH'

    # 读取数据
    #############################################################################################
    fund_nav = Fund().get_fund_factor("Repair_Nav")
    index_close = Index().get_index_factor(index_code, None, None, attr=['CLOSE'])
    index_close.columns = [index_code]

    result = pd.DataFrame([], index=fund_nav.columns, columns=['最近1年跟踪误差', '有效数据长度'])

    # 计算最近1年跟踪误差数据
    #############################################################################################
    fund_nav = fund_nav.ix[index_close.index, :]
    fund_pct = fund_nav.pct_change()
    index_pct = index_close.pct_change()
    index_pct = index_pct[index_code]
    fund_excess_pct = fund_pct.sub(index_pct, axis='index')
    fund_excess_pct_period = fund_excess_pct.ix[begin_date: end_date]
    result.ix[:, "有效数据长度"] = fund_excess_pct_period.count()
    result.ix[:, "最近1年跟踪误差"] = fund_excess_pct_period.std() * np.sqrt(250)

    # 筛选
    #############################################################################################
    result = result.dropna()
    result = result[result['有效数据长度'] > min_period]
    result = result[result['最近1年跟踪误差'] < track_error_up]

    code_str = ','.join(result.index)
    data = w.wss(code_str, "fund_benchmark,fund_fullname,fund_setupdate,fund_investtype")
    data_pd = pd.DataFrame(data.Data, index=data.Fields, columns=data.Codes).T
    data_pd.columns = ['基金基准', '基金全称', '上市日期', '基金类型']
    data_pd['上市日期'] = data_pd['上市日期'].map(lambda x: x.strftime('%Y-%m-%d'))
    result = pd.concat([data_pd, result], axis=1)
    result = result[result["基金基准"].map(lambda x: index_name in x)]
    result = result[result["上市日期"] < ipo_date]
    result = result[result["基金全称"].map(lambda x: "交易型开放式指数" not in x)]
    result = result[result["基金全称"].map(lambda x: "联接" not in x)]

    # 输出结果
    ############################################################################################
    out_path = os.path.join(out_path, "filter_fund_pool")
    num_format_pd = pd.DataFrame([], columns=result.columns, index=['format'])
    num_format_pd.ix['format', :] = '0.00'

    begin_row_number = 0
    begin_col_number = 1
    color = "red"
    file_name = os.path.join(out_path, '基金初次筛选池_' + index_name + '.xlsx')
    sheet_name = "基金筛选池"

    write_pandas(file_name, sheet_name, begin_row_number, begin_col_number, result, num_format_pd, color)
    #############################################################################################


if __name__ == '__main__':

    # 筛选沪深300增强基金池
    begin_date = '2017-07-15'
    end_date = '2018-07-15'
    ipo_date = '2017-07-15'
    min_period = 200
    track_error_up = 0.05
    index_name = '沪深300'
    index_code = '000300.SH'
    out_path = 'E:\\3_数据\\4_fund_data\\6_index_enhanced_fund_snowball\\'

    filter_fund_pool(index_code, begin_date, end_date, min_period,
                     ipo_date, track_error_up, index_name, out_path)

    track_error_up = 0.08
    index_name = '中证500'
    index_code = '000905.SH'
    filter_fund_pool(index_code, begin_date, end_date, min_period,
                     ipo_date, track_error_up, index_name,out_path)