import pandas as pd
from quant.utility_fun.write_pandas_to_excel import write_pandas
from quant.stock.date import Date
from quant.stock.index import Index
from quant.fund.fund import Fund
import os


def cal_exposure(beg_date, end_date, out_path):

    # beg_date = "20130629"
    # end_date = "20180715"
    # out_path = 'E:\\3_数据\\4_fund_data\\6_index_enhanced_fund_snowball\\'

    # 计算沪深300、中证500的暴露
    ##########################################################################################

    Index().cal_index_exposure_period("000300.SH", beg_date=beg_date, end_date=end_date)
    Index().cal_index_exposure_period("000905.SH", beg_date=beg_date, end_date=end_date)

    # 沪深300基金的暴露
    ##########################################################################################
    index_name = '沪深300'
    file = os.path.join(out_path, 'filter_fund_pool\\', '基金最终筛选池_' + index_name + '.xlsx')
    fund_code = pd.read_excel(file, index_col=[1], encoding='gbk')
    fund_code_list = list(fund_code.index)

    for i_fund in range(0, len(fund_code_list)):
        fund = fund_code_list[i_fund]
        print(fund)
        Fund().cal_fund_holder_exposure(fund=fund, beg_date=beg_date, end_date=end_date)

    # 中证500基金暴露
    ##########################################################################################
    index_name = '中证500'
    file = os.path.join(out_path, 'filter_fund_pool\\', '基金最终筛选池_' + index_name + '.xlsx')
    fund_code = pd.read_excel(file, index_col=[1], encoding='gbk')
    fund_code_list = list(fund_code.index)

    for i_fund in range(0, len(fund_code_list)):
        fund = fund_code_list[i_fund]
        print(fund)
        Fund().cal_fund_holder_exposure(fund=fund, beg_date=beg_date, end_date=end_date)
    ##########################################################################################


def concat_exposure(halfyear_date, out_path):

    # 参数
    ##########################################################################################
    # end_date = "20180715"
    # out_path = 'E:\\3_数据\\4_fund_data\\6_index_enhanced_fund_snowball\\'

    # 沪深300 指数、基金暴露拼接起来
    ##########################################################################################
    index_name = '沪深300'
    index_code = "000300.SH"
    index_exposure = Index().get_index_exposure_date(index_code, halfyear_date)
    file = os.path.join(out_path, 'filter_fund_pool\\', '基金最终筛选池_' + index_name + '.xlsx')
    fund_code = pd.read_excel(file, index_col=[1], encoding='gbk')
    fund_code_list = list(fund_code.index)

    for i_fund in range(0, len(fund_code_list)):
        fund = fund_code_list[i_fund]
        exposure_add = Fund().get_fund_holder_exposure_date(fund, halfyear_date)

        if i_fund == 0:
            exposure_fund = exposure_add
        else:
            exposure_fund = pd.concat([exposure_fund, exposure_add], axis=0)

    exposure = pd.concat([exposure_fund, index_exposure], axis=0)
    num_format_pd = pd.DataFrame([], columns=exposure.columns, index=['format'])
    num_format_pd.ix['format', :] = '0.00'

    begin_row_number = 0
    begin_col_number = 0
    color = "red"
    file_name = os.path.join(out_path, "exposure", index_name,
                            "BARRA风格暴露_" + index_name + "_" +
                             Date().get_normal_date_month_end_day(halfyear_date) + ".xlsx")
    sheet_name = "BARRA风格暴露"
    write_pandas(file_name, sheet_name, begin_row_number, begin_col_number, exposure, num_format_pd, color)

    ##########################################################################################
    index_name = '中证500'
    index_code = "000905.SH"
    index_exposure = Index().get_index_exposure_date(index_code, halfyear_date)
    file = os.path.join(out_path, 'filter_fund_pool\\', '基金最终筛选池_' + index_name + '.xlsx')
    fund_code = pd.read_excel(file, index_col=[1], encoding='gbk')
    fund_code_list = list(fund_code.index)

    for i_fund in range(0, len(fund_code_list)):
        fund = fund_code_list[i_fund]
        exposure_add = Fund().get_fund_holder_exposure_date(fund, halfyear_date)

        if i_fund == 0:
            exposure_fund = exposure_add
        else:
            exposure_fund = pd.concat([exposure_fund, exposure_add], axis=0)

    exposure = pd.concat([exposure_fund, index_exposure], axis=0)
    num_format_pd = pd.DataFrame([], columns=exposure.columns, index=['format'])
    num_format_pd.ix['format', :] = '0.00'

    begin_row_number = 0
    begin_col_number = 0
    color = "red"
    file_name = os.path.join(out_path, "exposure", index_name,
                            "BARRA风格暴露_" + index_name + "_" +
                             Date().get_normal_date_month_end_day(halfyear_date) + ".xlsx")
    sheet_name = "BARRA风格暴露"
    write_pandas(file_name, sheet_name, begin_row_number, begin_col_number, exposure, num_format_pd, color)
    ##########################################################################################


if __name__ == '__main__':

    beg_date = "20180101"
    end_date = "20180815"
    halfyear_date = "20171229"
    out_path = 'E:\\3_Data\\4_fund_data\\6_index_enhanced_fund_snowball\\'
    # cal_exposure(beg_date, end_date, out_path)
    concat_exposure(halfyear_date, out_path)

