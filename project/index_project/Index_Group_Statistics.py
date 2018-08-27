from quant.stock.index import Index
import numpy as np
import pandas as pd
from quant.utility_fun.write_pandas_to_excel import write_pandas


def Index_Group_Statistics(out_path, index_code, value_factor, group_number):

    # 0、输入参数
    ##############################################################################
    # out_path = 'C:\\Users\\doufucheng\\OneDrive\\Desktop\\data\\'
    # index_code = "000300.SH"
    # value_factor = 'PE_TTM'
    # group_number = 8

    # 1、原始数据整理
    ##############################################################################

    # 1、1: 读入指数收益率数据和pe
    ###################################
    data = Index().get_index_factor(index_code, None, None, ['PCT', value_factor])
    data = data.dropna(subset=[value_factor])
    data.columns = ['pct', 'pe']
    data['pe'] = data['pe'].round(2)
    year_number = 242

    # 1、2: 指数 日收益 累计收益
    ###################################
    data['ln_pct'] = np.log(data['pct'] + 1)
    data['cum_sum_pct'] = data['ln_pct'].cumsum().map(lambda x: np.exp(x)-1)

    # 1、3: 之后1、3、5年的收益
    ###################################
    data['return_1y'] = data['ln_pct'].rolling(window=year_number).sum().shift(-year_number)
    data['return_3y'] = data['ln_pct'].rolling(window=year_number*3).sum().shift(-year_number*3)
    data['return_5y'] = data['ln_pct'].rolling(window=year_number*5).sum().shift(-year_number*5)

    # 1、4: 之后1、3、5年的收益是否大于0
    ###################################
    data['if_zero_1y'] = data['return_1y'] > 0.0
    data['if_zero_3y'] = data['return_3y'] > 0.0
    data['if_zero_5y'] = data['return_5y'] > 0.0

    # 1、5: 在全局的pe百分比
    ###################################
    data['rank'] = data['pe'].rank() / len(data)
    data['rank'] *= 100
    data['rank'] = data['rank'].round(0)

    # 1、7: 之后1年超过初始PE的时间
    ###################################
    for i in range(0, len(data) - year_number):
        init_pe = data.ix[i, "pe"]
        data_bigger = data.ix[i:i+year_number, 'pe'] > init_pe
        data_bigger = data_bigger[data_bigger]
        ratio = len(data_bigger) / year_number
        data.ix[i, 'if_1y_ratio'] = ratio

    # 1、8: 之后3年超过初始PE的时间
    ###################################
    for i in range(0, len(data) - year_number*3):
        init_pe = data.ix[i, "pe"]
        data_bigger = data.ix[i:i+year_number*3, 'pe'] > init_pe
        data_bigger = data_bigger[data_bigger]
        ratio = len(data_bigger) / (year_number*3)
        data.ix[i, 'if_3y_ratio'] = ratio

    # 1、9: 之后5年超过初始PE的时间
    ###################################
    for i in range(0, len(data) - year_number*5):
        init_pe = data.ix[i, "pe"]
        data_bigger = data.ix[i:i+year_number*5, 'pe'] > init_pe
        data_bigger = data_bigger[data_bigger]
        ratio = len(data_bigger) / (year_number*5)
        data.ix[i, 'if_5y_ratio'] = ratio

    data['pe_cut'] = pd.qcut(data['pe'], group_number)
    data.to_csv(out_path + index_code + '_原始数据.csv')

    # 2、分组统计
    ##############################################################################

    # 2、1: 1年后 收益中位数、pe超过初始PE的百分比、有效数字的个数
    ########################################################
    my_data = data.dropna(subset=['return_1y'])
    my_data['pe_cut'] = pd.qcut(data['pe'], group_number)
    if_pe_1y_ratio = my_data.groupby(by=['pe_cut'])['if_1y_ratio'].mean()
    return_1y_median = my_data.groupby(by=['pe_cut'])['return_1y'].median()
    return_1y_count = my_data.groupby(by=['pe_cut'])['return_1y'].count()
    my_data['pe_rank_cut'] = pd.qcut(data['rank'], group_number)
    return_pe_rank = my_data.groupby(by=['pe_rank_cut'])['return_1y'].median()
    return_pe_rank = pd.DataFrame(return_pe_rank.index.values.to_dense(),
                                     index=return_1y_median.index.values.to_dense(), columns=['历史百分位数'])
    return_pe_rank['开始时间'] = data.index[0]
    return_pe_rank['结束时间'] = data.index[-1]
    return_pe_rank['当前PE'] = data.ix[-1, 'pe']

    # 1年后 收益大于0的百分比
    if_zero_number = my_data.groupby(by=['pe_cut'])['if_zero_1y'].sum()
    sum_number = my_data.groupby(by=['pe_cut'])['if_zero_1y'].count()
    zero_ratio_1y = pd.DataFrame(if_zero_number / sum_number)

    # 2、1: 3年后 收益中位数、pe超过初始PE的百分比、有效数字的个数
    #######################################################

    my_data = data.dropna(subset=['return_3y'])
    my_data['pe_cut'] = pd.qcut(data['pe'], group_number)
    if_pe_3y_ratio = my_data.groupby(by=['pe_cut'])['if_3y_ratio'].median()
    return_3y_median = my_data.groupby(by=['pe_cut'])['return_3y'].median()
    return_3y_count = my_data.groupby(by=['pe_cut'])['return_3y'].count()

    if_zero_number = my_data.groupby(by=['pe_cut'])['if_zero_3y'].sum()
    sum_number = my_data.groupby(by=['pe_cut'])['if_zero_3y'].count()
    zero_ratio_3y = pd.DataFrame(if_zero_number / sum_number)

    # 2、3: 5年后 收益中位数、pe超过初始PE的百分比、有效数字的个数
    #######################################################
    my_data = data.dropna(subset=['return_5y'])
    my_data['pe_cut'] = pd.qcut(data['pe'], group_number)
    if_pe_5y_ratio = my_data.groupby(by=['pe_cut'])['if_5y_ratio'].median()
    return_5y_median = my_data.groupby(by=['pe_cut'])['return_5y'].median()
    return_5y_count = my_data.groupby(by=['pe_cut'])['return_5y'].count()

    if_zero_number = my_data.groupby(by=['pe_cut'])['if_zero_5y'].sum()
    sum_number = my_data.groupby(by=['pe_cut'])['if_zero_5y'].count()
    zero_ratio_5y = pd.DataFrame(if_zero_number / sum_number)

    # 数据输出
    ##############################################################################

    res = pd.concat([return_pe_rank, return_1y_count, return_3y_count, return_5y_count,
                     return_1y_median, return_3y_median, return_5y_median,
                     zero_ratio_1y, zero_ratio_3y, zero_ratio_5y,
                     if_pe_1y_ratio, if_pe_3y_ratio, if_pe_5y_ratio
                     ], axis=1)
    res.index.name = "PE绝对值范围"
    res.columns = ["PE百分位范围", '开始时间','结束时间', '当前PE',
                   '有效数据个数_1y', '有效数据个数_3y', '有效数据个数_5y',
                   '收益中位数_1y', '收益中位数_3y', '收益中位数_5y',
                   '收益大于0的比例_1y', '收益大于0的比例_3y', '收益大于0的比例_5y',
                   '超过初始PE天数的比例的中位数_1y', '超过初始PE天数的比例的中位数_3y', '超过初始PE天数的比例的中位数_5y']

    res.index = res.index.values.to_dense()
    res.index.name = "PE绝对值范围"

    num_format_pd = pd.DataFrame([], columns=res.columns, index=['format'])
    num_format_pd.ix['format', :] = '0.00%'
    num_format_pd.ix['format', ['开始时间','结束时间', '当前PE',
                                '有效数据个数_1y', '有效数据个数_3y', '有效数据个数_5y']] = '0.0'

    begin_row_number = 0
    begin_col_number = 1
    color = "red"
    file_name = out_path + index_code + '_收益中位数.xlsx'
    sheet_name = "收益中位数"

    write_pandas(file_name, sheet_name, begin_row_number, begin_col_number, res, num_format_pd, color)


if __name__ == '__main__':

    out_path = 'C:\\Users\\doufucheng\\OneDrive\\Desktop\\data\\'
    index_code_list = ["399985.SZ", "000300.SH", '000905.SH', 'HSI.HI', 'SPX.GI', '881001.WI', '399005.SZ', '399006.SZ']
    value_factor = 'PE_TTM'
    group_number = 8

    for i in range(0, len(index_code_list)):
        index_code = index_code_list[i]
        Index_Group_Statistics(out_path, index_code, value_factor, group_number)

