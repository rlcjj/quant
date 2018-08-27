import pandas as pd
from WindPy import w
w.start()
from quant.utility_fun.write_pandas_to_excel import write_pandas


def score_quarter(x, val_25, val_75):

    if x > val_75:
        r = 5
    elif x < val_25:
        r = 0
    else:
        r = 5 * (x - val_25) / (val_75 - val_25)
    return r


def score_quarter_reverse(x, val_25, val_75):

    if x > val_75:
        r = 0
    elif x < val_25:
        r = 5
    else:
        r = 5 - (5 * (x - val_25) / (val_75 - val_25))
    return r


def score_ex(x):

    if x < 0.1:
        return 1
    elif x < 0.2:
        return 0.75
    elif x < 0.4:
        return 0.5
    elif x < 0.6:
        return 0.25
    else:
        return 0


def fund_score_date(end_date, halfyear_date, index_name, index_code, path):

    # 参数
    ##################################################################################################################
    # report_date = "2017-12-31"
    # report_date_last = "2017-06-30"
    # index_name = '中证500'
    # path = 'E:\\4_代码\\pycharmprojects\\31_雪球优选增强基金\\output_data\\'

    # 读取数据 基金指标 和 风格暴露
    ##################################################################################################################
    sub_path = path + 'cal_fund_factor\\' + index_name + '\\'
    filename = sub_path + '基金指标_' + index_name + '_' + end_date + '.xlsx'
    fund_factor = pd.read_excel(filename, index_col=[0], encoding='gbk')

    # 超额收益小于0的不参与基金打分
    # fund_factor = fund_factor[fund_factor['最近1年超额收益'] > -1.0]

    sub_path = path + 'exposure\\' + index_name + '\\'
    filename = sub_path + 'BARRA风格暴露_' + index_name + '_' + halfyear_date + '.xlsx'
    exposure = pd.read_excel(filename, index_col=[0], encoding='gbk')

    exposure = exposure - exposure.ix[index_code, :]
    exposure = exposure.abs()
    exp_col = ['贝塔', '账面市值比', '盈利', '成长', '杠杆', '流动性', '动量', '残差波动率', '市值', '非线性市值']
    exposure.columns = exp_col
    exposure = exposure.round(2)

    # 计算跟踪误差得分
    ##################################################################################################################

    result = pd.DataFrame([], index=fund_factor.index)

    result.ix[:, '基金名称'] = fund_factor.ix[:, '基金简称']
    result.ix[:, '上期超额收益'] = fund_factor.ix[:, '最近1年超额收益']
    result.ix[:, '下期超额收益'] = fund_factor.ix[:, '之后半年超额收益']

    if index_name == '中证500':
        val_25 = max(0.03, fund_factor.ix[:, '最近1年跟踪误差'].quantile(0.20))
        val_75 = min(0.08, fund_factor.ix[:, '最近1年跟踪误差'].quantile(0.80))
    else:
        val_25 = max(0.02, fund_factor.ix[:, '最近1年跟踪误差'].quantile(0.20))
        val_75 = min(0.05, fund_factor.ix[:, '最近1年跟踪误差'].quantile(0.80))

    result.ix[:, '跟踪误差'] = fund_factor.ix[:, '最近1年跟踪误差']
    result.ix[:, '跟踪误差得分'] = fund_factor.ix[:, '最近1年跟踪误差'].map(lambda x: score_quarter_reverse(x, val_25, val_75)).round(2)

    # 计算超额收益得分
    ##################################################################################################################
    if index_name == '中证500':
        val_25 = max(0.00, fund_factor.ix[:, '最近1年超额收益'].quantile(0.20))
        val_75 = min(0.15, fund_factor.ix[:, '最近1年超额收益'].quantile(0.80))

    else:
        val_25 = max(0.00, fund_factor.ix[:, '最近1年超额收益'].quantile(0.20))
        val_75 = min(0.10, fund_factor.ix[:, '最近1年超额收益'].quantile(0.80))

    result.ix[:, '超额收益'] = fund_factor.ix[:, '最近1年超额收益']
    result.ix[:, '超额收益得分'] = fund_factor.ix[:, '最近1年超额收益'].map(lambda x: score_quarter(x, val_25, val_75)).round(2)

    # 计算信息比率得分
    ##################################################################################################################
    val_25 = fund_factor.ix[:, '最近1年信息比率'].quantile(0.20)
    val_75 = fund_factor.ix[:, '最近1年信息比率'].quantile(0.80)

    result.ix[:, '信息比率'] = fund_factor.ix[:, '最近1年信息比率'].round(2)
    result.ix[:, '信息比率得分'] = fund_factor.ix[:, '最近1年信息比率'].map(lambda x: score_quarter(x, val_25, val_75)).round(2)

    # 计算风格偏露得分
    ##################################################################################################################
    result = pd.concat([result, exposure.iloc[:, 0:10]], axis=1)
    result = result.dropna(subset=["基金名称"])

    result.ix[:, '风格暴露得分'] = 0.0

    for i_col in range(10):

        col = exposure.columns[i_col]
        result.ix[:, '风格暴露得分'] += result.ix[:, col].map(score_ex)

    result.ix[:, '风格暴露得分'] = result.ix[:, '风格暴露得分'] * 0.5

    val_25 = result.ix[:, '风格暴露得分'].quantile(0.20)
    val_75 = result.ix[:, '风格暴露得分'].quantile(0.80)

    result.ix[:, '风格暴露得分'] = result.ix[:, '风格暴露得分'].map(lambda x: score_quarter(x, val_25, val_75)).round(2)

    # 计算总得分
    ##################################################################################################################
    if index_name == "中证500":
        result.ix[:, '总得分'] = result['跟踪误差得分'] * 0.10 + result['超额收益得分'] * 0.40 + \
                              result['信息比率得分'] * 0.20 + result['风格暴露得分'] * 0.30
    else:
        # result.ix[:, '总得分'] = result['跟踪误差得分'] * 0.05 + result['超额收益得分'] * 0.50 + \
        #                       result['信息比率得分'] * 0.30 + result['风格暴露得分'] * 0.15

        result.ix[:, '总得分'] = result['跟踪误差得分'] * 0.10 + result['超额收益得分'] * 0.40 + \
                              result['信息比率得分'] * 0.20 + result['风格暴露得分'] * 0.30
    result = result.sort_values(by=['总得分'], ascending=False)

    col = ["基金名称", "下期超额收益", '总得分', '跟踪误差', '跟踪误差得分',
           '超额收益', '超额收益得分', '信息比率', '信息比率得分', '风格暴露得分', '上期超额收益']
    col.extend(exp_col[0:10])
    result = result[col]

    # 写到EXCEL表
    ##################################################################################################################
    num_format_pd = pd.DataFrame([], columns=result.columns, index=['format'])
    num_format_pd.ix['format', :] = '0.00'
    num_format_pd.ix['format', ['跟踪误差', '超额收益', '下期超额收益', '上期超额收益']] = '0.00%'
    begin_row_number = 0
    begin_col_number = 0
    color = "red"
    file_name = path + 'score_fund\\' + index_name + '\\' + '基金得分_' + index_name + '_' + end_date + '.xlsx'
    sheet_name = "基金得分"
    write_pandas(file_name, sheet_name, begin_row_number, begin_col_number, result, num_format_pd, color)
    ##################################################################################################################


def score_fund(end_date, halfyear_date, path):

    # 参数
    ##################################################################################################################
    # path = 'E:\\3_数据\\4_fund_data\\6_index_enhanced_fund_snowball\\'
    # end_date = "20180715"
    # halfyear_date = "20171229"

    # 中证500
    ##################################################################################################################
    index_name = '中证500'
    index_code = '000905.SH'

    fund_score_date(end_date, halfyear_date, index_name, index_code, path)

    # 沪深300
    ##################################################################################################################
    index_name = '沪深300'
    index_code = '000300.SH'
    fund_score_date(end_date, halfyear_date, index_name, index_code, path)

    return True


if __name__ == '__main__':

    path = 'E:\\3_Data\\4_fund_data\\6_index_enhanced_fund_snowball\\'
    end_date = "20180815"
    halfyear_date = "20171229"
    score_fund(end_date, halfyear_date, path)
