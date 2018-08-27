import os
from datetime import datetime
import pandas as pd
from quant.project.mfc_holding_project.attribute_mfcteda.CalStockReturnDaily import CalStockReturnDaily
from quant.mfc.mfc_data import MfcData
from quant.project.mfc_holding_project.attribute_mfcteda.CalNewStockReturnDaily import CalNewStockReturnDaily
from quant.stock.date import Date
from quant.stock.index import Index
from quant.stock.stock import Stock
from quant.utility_fun.write_excel import WriteExcel


def AttributeMfctedaFund(index_code_ratio, fund_code, index_code,
                         fund_name, beg_date, end_date, fund_id,
                         path, type, mg_fee_ratio):

    """
    将某只基金 一段时间内 每日净值涨跌 拆分
    """

    # 参数举例
    ######################################################################################
    # index_code_ratio = 0.95
    # fund_code = '162216.OF'
    # index_code = '000905.SH'
    # fund_name = '泰达中证500指数分级'
    # beg_date = '20180101'
    # end_date = '20180731'
    # fund_id = 38
    # path = 'C:\\Users\\doufucheng\\OneDrive\\Desktop\\data\\'
    # type = '专户'

    # 读取基金复权涨跌幅
    ################################################################################################
    beg_date = Date().get_trade_date_offset(beg_date, -0)

    if type == "专户":
        fund_pct = MfcData().get_fund_nav_adjust(fund_name, Date().get_trade_date_offset(beg_date, -2), end_date)
        fund_pct['基金涨跌幅'] = fund_pct['累计复权净值'].pct_change()
    else:
        fund_pct = MfcData().get_mfcteda_public_fund_pct_wind(fund_code, beg_date, end_date)
        fund_pct.columns = ['基金涨跌幅']

    # 指数收益 持仓数据
    # 净值 = 股票资产 + 债券资产 + 基金资产 + 回购资产 + 当前现金余额 + 累计应收 - 累计应付
    # 累计应收 和 累计应付 代表 每日申赎 计提 交易管理费用等 未结算至现金的部分
    # 这里并没有按照每日拆分净值的方式计算 而是按照每日拆分当日总浮动盈亏 = 前日净值 * 当日基金复权涨跌幅
    ################################################################################################
    index_pct = Index().get_index_factor(index_code, Date().get_trade_date_offset(beg_date, -1), end_date, ['CLOSE'])
    index_pct = index_pct.pct_change()
    index_pct.columns = ['指数涨跌幅']
    fund_asset = MfcData().get_fund_asset_period(fund_id, beg_date, end_date)
    close_unadjust = Stock().get_factor_h5("Price_Unadjust", None, "primary_mfc")
    adjust_factor = Stock().get_factor_h5("AdjustFactor", None, "primary_mfc")
    fund_asset['股票资产-汇总'] = fund_asset['股票资产']

    data = pd.concat([fund_pct, index_pct, fund_asset], axis=1)
    data = data.dropna(subset=['基金涨跌幅', '指数涨跌幅'])

    data['昨日净值'] = data['净值'].shift(1)
    data['昨日基金份额'] = data['基金份额'].shift(1)
    data['昨日单位净值'] = data['单位净值'].shift(1)

    # 计算 每一日 新股收益 股票收益
    ################################################################################################
    date_series = Date().get_trade_date_series(beg_date, end_date)

    for i_date in range(len(date_series)):

        date = date_series[i_date]
        new_stock_return, new_stock_asset = CalNewStockReturnDaily(fund_name, date,
                                                                   path, close_unadjust,
                                                                   adjust_factor, cal_type="close")
        stock_return, mg_fee, trade_fee, stock_asset = CalStockReturnDaily(fund_name, date, path, close_unadjust,
                                                                           adjust_factor, mg_fee_ratio,
                                                                           cal_type="close")
        data.loc[date, '新股资产'] = new_stock_asset
        data.loc[date, '股票资产'] = stock_asset
        data.loc[date, '新股盈亏'] = new_stock_return
        data.loc[date, '股票盈亏'] = stock_return
        data.loc[date, '管理托管费用'] = mg_fee
        data.loc[date, '交易印花费用'] = trade_fee

        new_stock_return, new_stock_asset = CalNewStockReturnDaily(fund_name, date, path, close_unadjust,
                                                                   adjust_factor, cal_type="average")
        stock_return, mg_fee, trade_fee, stock_asset = CalStockReturnDaily(fund_name, date, path, close_unadjust,
                                                                           adjust_factor, mg_fee_ratio,
                                                                           cal_type="average")
        data.loc[date, '新股盈亏-TradePrice'] = new_stock_return
        data.loc[date, '股票盈亏-TradePrice'] = stock_return

    data = data.dropna(subset=['基金涨跌幅', '指数涨跌幅'])
    data[['新股盈亏', '当日股票总盈亏金额']] = data[['新股盈亏', '当日股票总盈亏金额']].fillna(0.0)
    data = data[data['股票资产'] > 0.0]
    data['股票仓位'] = data['股票资产'] / data['净值']
    data['昨日股票仓位'] = data['股票仓位'].shift(1)

    # 资产盈亏 = 股票盈亏 + 新股盈亏 + 债券其他 + 托管管理费 + 交易印花费
    ################################################################################################
    cols = ['管理托管费用', '交易印花费用', '股票盈亏', '新股盈亏']
    data[cols] = data[cols].fillna(0.0)
    data['汇总盈亏'] = data['管理托管费用'] + data['交易印花费用'] + data['股票盈亏'] + data['新股盈亏']
    data['日内交易盈亏'] = data['股票盈亏'] - data['股票盈亏-TradePrice'] + data['新股盈亏'] - data['新股盈亏-TradePrice']
    data['资产盈亏'] = data['基金涨跌幅'] * data['昨日净值']
    data['固收其他盈亏'] = data['资产盈亏'] - data['汇总盈亏'] - data['日内交易盈亏']
    data['昨日股票资产'] = data['股票资产'].shift(1)
    data['股票涨跌幅'] = data['股票盈亏'] / data['昨日股票资产']

    # 股票盈亏 = 基准盈亏 + 超额盈亏
    ################################################################################################
    data['基准盈亏'] = data['指数涨跌幅'] * data['昨日净值'] * index_code_ratio
    data['超额盈亏'] = data['昨日股票仓位'] * data['股票涨跌幅'] * data['昨日净值'] - data['基准盈亏']

    # 超额盈亏 = 择时（资产配置能力） + 选股能力
    ################################################################################################
    data['择时盈亏'] = (data['昨日股票仓位'] - index_code_ratio) * data['指数涨跌幅'] * data['昨日净值']
    data['选股盈亏'] = data['昨日股票仓位'] * (data['股票涨跌幅'] - data['指数涨跌幅']) * data['昨日净值']
    data['全仓选股盈亏'] = (data['股票涨跌幅'] - data['指数涨跌幅']) * data['昨日净值']

    # 以单位净值计算
    ################################################################################################
    data['净值-资产盈亏'] = data['资产盈亏'] / data['昨日基金份额']
    data['净值-管理托管费用'] = data['管理托管费用'] / data['昨日基金份额']
    data['净值-交易印花费用'] = data['交易印花费用'] / data['昨日基金份额']
    data['净值-股票盈亏'] = data['股票盈亏'] / data['昨日基金份额']
    data['净值-新股盈亏'] = data['新股盈亏'] / data['昨日基金份额']
    data['净值-固收其他盈亏'] = data['固收其他盈亏'] / data['昨日基金份额']
    data['净值-日内交易盈亏'] = data['日内交易盈亏'] / data['昨日基金份额']
    data['净值-基准盈亏'] = data['基准盈亏'] / data['昨日基金份额']
    data['净值-超额盈亏'] = data['超额盈亏'] / data['昨日基金份额']
    data['净值-择时盈亏'] = data['择时盈亏'] / data['昨日基金份额']
    data['净值-选股盈亏'] = data['选股盈亏'] / data['昨日基金份额']
    data['净值-全仓选股盈亏'] = data['全仓选股盈亏'] / data['昨日基金份额']

    index = ['净值-资产盈亏', '净值-股票盈亏', '净值-新股盈亏', '净值-固收其他盈亏', '净值-日内交易盈亏', '净值-管理托管费用',
             '净值-交易印花费用', '净值-基准盈亏', '净值-超额盈亏', '净值-择时盈亏', '净值-选股盈亏', '净值-全仓选股盈亏']

    # 按照 百分比 收益率计算
    ################################################################################################
    data = data.dropna(subset=['昨日单位净值'])
    nav = data.loc[data.index[0], '昨日单位净值']
    pct = data['净值-资产盈亏'].sum() / nav
    result = pd.DataFrame([], columns=['净值变化', '百分比', '收益率'], index=index)

    result.loc[index, '净值变化'] = data.loc[:, index].sum()
    result.loc[index, '百分比'] = result.loc[index, '净值变化'] / result.loc['净值-资产盈亏', '净值变化']
    result.loc[index, '收益率'] = result.loc[index, '百分比'] * pct

    # 年化收益率 开始时间 结束时间
    ################################################################################################
    result.index = ['基金整体', '股票部分', '新股部分', '固收+其他部分', "日内交易部分", '管理托管',
                    '交易印花', '股票基准', '股票超额', '股票择时', '股票选股', '全仓股票选股']
    days = (datetime.strptime(end_date, '%Y%m%d') - datetime.strptime(beg_date, '%Y%m%d')).days
    result.loc[:, '年化收益'] = result.loc[:, '收益率'].map(lambda x: (x + 1) ** (365 / days) - 1.0)
    result.loc['股票仓位', :] = data['股票仓位'].mean()
    result.loc['开始时间', :] = data.index[0]
    result.loc['结束时间', :] = data.index[-1]
    ################################################################################################

    # 写入每天的拆分
    ####################################################################################################################
    num_format_pd = pd.DataFrame([], columns=data.columns, index=['format'])
    num_format_pd.ix['format', :] = '0.00'
    num_format_pd.ix['format', ['基金涨跌幅', '指数涨跌幅', '股票仓位', '昨日股票仓位', '股票涨跌幅']] = '0.00%'
    num_format_pd.ix['format', ['单位净值', '昨日单位净值', '净值-管理托管费用', '净值-交易印花费用',
                                '净值-股票盈亏', '净值-新股盈亏', '净值-固收其他盈亏', '净值-基准盈亏',
                                '净值-择时盈亏', '净值-选股盈亏', '净值-资产盈亏', '净值-全仓选股盈亏']] = '0.0000'

    begin_row_number = 0
    begin_col_number = 1
    color = "red"
    save_path = os.path.join(path, fund_name, "整体")
    file_name = os.path.join(save_path, "归因_" + fund_name + '_' + str(data.index[0]) + '_' + str(data.index[-1]) + ".xlsx")
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    sheet_name = fund_name
    excel = WriteExcel(file_name)
    worksheet = excel.add_worksheet(sheet_name)
    excel.write_pandas(data, worksheet, begin_row_number=begin_row_number, begin_col_number=begin_col_number,
                       num_format_pd=num_format_pd, color=color, fillna=True)
    excel.close()

    # 写入汇总的拆分
    ####################################################################################################################
    num_format_pd = pd.DataFrame([], columns=result.columns, index=['format'])
    num_format_pd.ix['format', :] = '0.00%'
    num_format_pd.ix['format', ['净值变化']] = '0.0000'

    begin_row_number = 0
    begin_col_number = 1
    color = "red"
    save_path = os.path.join(path, fund_name, "整体")
    file_name = os.path.join(save_path, "归因汇总_" + fund_name + '_' + str(data.index[0]) + '_' + str(data.index[-1]) + ".xlsx")
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    sheet_name = fund_name
    excel = WriteExcel(file_name)
    worksheet = excel.add_worksheet(sheet_name)
    excel.write_pandas(result, worksheet, begin_row_number=begin_row_number, begin_col_number=begin_col_number,
                       num_format_pd=num_format_pd, color=color, fillna=True)
    excel.close()
    ####################################################################################################################


if __name__ == '__main__':

    # 参数文件读取参数
    ####################################################################################################################
    param_path = 'E:\\3_Data\\6_mfcteda_fund_data\\2_Mfc_Fund\\'
    param_file = param_path + 'Fund_Info.xlsx'
    param = pd.read_excel(param_file, index_col=[0])
    data_path = 'C:\\Users\\doufucheng\\OneDrive\\Desktop\\data\\'

    # 所需要计算的基金 和 开始结束日期
    ####################################################################################################################
    number_list = range(0, len(param))
    number_list = [9, 6]
    date_list = [ # ["20160101", '20161231'],
                 ["20170101", '20171231'],
                 ["20180101", '20180731']]

    # 开始循环计算
    ####################################################################################################################
    for i_date in range(len(date_list)):

        beg_date = date_list[i_date][0]
        end_date = date_list[i_date][1]

        for i_fund in number_list:

            fund_name = param.index[i_fund]
            index_code_ratio = param.loc[fund_name, "Index_Ratio"]
            fund_code = param.loc[fund_name, "Code"]
            index_code = param.loc[fund_name, "Index"]
            fund_id = param.loc[fund_name, "Id"]
            type = param.loc[fund_name, "Type"]
            mg_fee_ratio = param.loc[fund_name, "MgFeeRatio"] + param.loc[fund_name, "TrusteeShipFeeRatio"]

            # 若基准不是NAN 就开始计算归因
            if len(str(index_code)) > 6:
                print(" ########## BEGIN ATTRIBUTE Fund %s Date From %s To %s" % (fund_name, beg_date, end_date))
                AttributeMfctedaFund(index_code_ratio, fund_code, index_code,
                                        fund_name, beg_date, end_date, fund_id, data_path, type, mg_fee_ratio)

    ####################################################################################################################
