from quant.mfc.mfc_data import MfcData
from quant.stock.date import Date
from quant.stock.stock import Stock
from quant.utility_fun.code_format import stock_code_add_postfix
import pandas as pd
import numpy as np
from datetime import datetime
import os
from quant.utility_fun.write_excel import WriteExcel


def CalStockReturnDaily(fund_name, date, path,
                        close_unadjust, adjust_factor, mg_fee_ratio, cal_type="close"):

    """
    1、计算当日净值变动中 有多少是股票（非新股）涨跌所带来的
       这里需要注意到是股票 送转分红 带来的影响 （利用前后两日的复权因子）
    2、顺便再计算股票的 管理托管费（当日净值*管理费率） 和 交易佣金（当日股票成交额*交易费率，包括新股）

    股票涨跌收益 有两种 计算方式
    1、1 股票以当日收盘价买卖  或者继续当日持有 股票收益 = 昨日收盘数量 * 当日收盘价格
    1、2 股票以当日均价买卖    或者继续当日持有 股票收益 = 当日持有股票收益 + 当日卖出股票收益 + 当日买入股票收益

    """

    # 计算参数
    ##########################################################################################
    mg_fee_ratio = mg_fee_ratio / 250

    # 印花税 + 交易佣金 + 冲击成本 (双边)
    double_fee_ratio = 0.001 + 0.0008 * 2 + 0.001 * 2
    pre_date = Date().get_trade_date_offset(date, -1)
    ipo_days = 40

    # 读取持仓数据
    ##########################################################################################
    try:
        security = MfcData().get_fund_security(date)
        security_pre_date = MfcData().get_fund_security(pre_date)
        trade = MfcData().get_trade_statement(date)
        total_asset = MfcData().get_fund_asset(date)
    except:
        print('The Holding Data For Stock Return Of Fund %s At Date %s is Null ' % (fund_name, date))
        return np.nan, np.nan, np.nan, np.nan

    # 读取价格数据
    ##########################################################################################

    try:
        close_unadjust_date = close_unadjust[date]
        close_unadjust_pre_date = close_unadjust[pre_date]
        adjust_factor_date = adjust_factor[date]
        adjust_factor_pre_date = adjust_factor[pre_date]
        ipo = Stock().get_ipo_date()
    except:
        print('The Price Data For Stock Return Of Fund %s At Date %s is Null ' % (fund_name, date))
        return np.nan, np.nan, np.nan, np.nan

    # 整理 持仓数据 价格数据
    ##########################################################################################

    #  当日交易的股票
    ##########################################################################################
    trade_data = trade[trade['基金名称'] == fund_name]
    trade_data = trade_data[trade_data['资产类别'] == '股票资产']
    trade_data = trade_data[['基金名称', '证券名称', '成交数量', '市场成交均价', '委托方向', '证券代码']]
    trade_data['证券代码'] = trade_data['证券代码'].map(stock_code_add_postfix)
    trade_data.index = trade_data['证券代码'].values
    trade_data = trade_data[['成交数量', '市场成交均价', '委托方向']]
    trade_data.columns = ['TradeVol', 'TradePrice', 'SellOrBuy']
    trade_data = trade_data[~trade_data.index.duplicated()]
    sell_code_list = list(trade_data[trade_data['SellOrBuy'] == "卖出"].index)
    trade_data.ix[sell_code_list, 'TradeVol'] = - trade_data.ix[sell_code_list, 'TradeVol']

    # 当日股票持仓
    ##########################################################################################
    security_data = security[security['基金名称'] == fund_name]
    security_data = security_data[security_data['证券类别'] == '股票']
    security_data = security_data[['基金名称', '证券名称', '持仓', '证券代码']]
    security_data['证券代码'] = security_data['证券代码'].map(stock_code_add_postfix)
    security_data.index = security_data['证券代码'].values
    security_data = security_data[['证券名称', '持仓']]
    security_data.columns = ['CodeName', 'TodayVol']

    # 前日股票持仓
    ##########################################################################################
    security_pre_date_data = security_pre_date[security_pre_date['基金名称'] == fund_name]
    security_pre_date_data = security_pre_date_data[security_pre_date_data['证券类别'] == '股票']
    security_pre_date_data = security_pre_date_data[['基金名称', '证券名称', '持仓', '证券代码']]
    security_pre_date_data['证券代码'] = security_pre_date_data['证券代码'].map(stock_code_add_postfix)
    security_pre_date_data.index = security_pre_date_data['证券代码'].values
    security_pre_date_data = security_pre_date_data['持仓']
    security_pre_date_data.name = 'YestodayVol'

    # 收盘价和复权因子
    ##########################################################################################
    adjust_factor = adjust_factor_date / adjust_factor_pre_date
    close_2_days = pd.concat([close_unadjust_date, close_unadjust_pre_date, adjust_factor], axis=1)
    close_2_days.columns = ['Close', 'PreClose', 'AdjustFactor']

    holding = pd.concat([security_data, trade_data, security_pre_date_data], axis=1)
    all_data = pd.concat([holding, close_2_days], axis=1)
    all_data = all_data.dropna(subset=['YestodayVol'])
    all_data = pd.concat([all_data, ipo['IPO_DATE']], axis=1)

    if cal_type == 'close':

        # 若当日股票均已今日收盘价卖出 计算当日股票收益
        ##########################################################################################
        price_change = all_data['Close'] - all_data['PreClose'] / all_data['AdjustFactor']
        all_data['StockReturn'] = all_data['YestodayVol'] * price_change

        all_data = all_data.dropna(subset=['StockReturn'])
        ipo_date = Date().get_trade_date_offset(date, -ipo_days)
        all_data = all_data[all_data['IPO_DATE'] < ipo_date]
        all_data = all_data[all_data['IPO_DATE'] <= date]

    else:

        # 分别计算当日新买入股票的收益 这两日持仓未变动的股票的收益 和当日卖出股票的收益
        ##########################################################################################
        sell_code_list = list(all_data[all_data['SellOrBuy'] == "卖出"].index)
        buy_code_list = list(all_data[all_data['SellOrBuy'] == "买入"].index)

        all_data[['TradeVol', 'TodayVol']] = all_data[['TradeVol', 'TodayVol']].fillna(0.0)
        all_data['HoldVol'] = all_data['TodayVol']
        today_vol = all_data.loc[buy_code_list, 'TodayVol']
        trade_vol = all_data.loc[buy_code_list, 'TradeVol']
        all_data.loc[buy_code_list, 'HoldVol'] = today_vol - trade_vol
        price_change = all_data['Close'] * all_data['AdjustFactor'] - all_data['PreClose']
        all_data['HoldReturn'] = all_data['HoldVol'] * price_change

        buy_vol = all_data.ix[buy_code_list, 'TradeVol'].abs()
        buy_return = buy_vol * (all_data.ix[buy_code_list, 'Close'] - all_data.ix[buy_code_list, 'TradePrice'])
        all_data.loc[buy_code_list, "BuyReturn"] = buy_return

        sell_vol = all_data.ix[sell_code_list, 'TradeVol'].abs()
        sell_price = all_data.ix[sell_code_list, 'TradePrice'] * all_data.ix[sell_code_list, 'AdjustFactor']
        sell_return = sell_vol * (sell_price - all_data.ix[sell_code_list, 'PreClose'])
        all_data.ix[sell_code_list, "SellReturn"] = sell_return

        columns = ['HoldReturn', 'BuyReturn', 'SellReturn']
        all_data[columns] = all_data[columns].fillna(0.0)
        all_data['StockReturn'] = all_data[columns].sum(axis=1)

        all_data = all_data.dropna(subset=['StockReturn'])
        ipo_date = Date().get_trade_date_offset(date, -ipo_days)
        all_data = all_data[all_data['IPO_DATE'] < ipo_date]
        all_data = all_data[all_data['IPO_DATE'] <= date]

    # 计算 交易费用 和 管理费用
    ##########################################################################################
    total_asset_fund = total_asset[total_asset['基金名称'] == fund_name]
    try:
        mg_fee = - total_asset_fund['净值'].values[0] * mg_fee_ratio
    except:
        mg_fee = np.nan

    trade_asset = (all_data['TradePrice'] * all_data['TradeVol'].abs()).sum()
    trade_fee = - trade_asset * double_fee_ratio / 2.0

    # 非新股的股票 当日收盘资产 和 假设当日收盘卖出的 股票收益
    ##########################################################################################

    if len(all_data) > 0:
        stock_return = all_data['StockReturn'].sum()
        stock_asset = (all_data['Close'] * all_data['TodayVol']).sum()

        # 每日的计算文件存储
        ################################################################################################################
        sub_path = os.path.join(path, fund_name, "股票")
        if not os.path.exists(sub_path):
            os.makedirs(sub_path)

        num_format_pd = pd.DataFrame([], columns=all_data.columns, index=['format'])
        num_format_pd.ix['format', :] = '0.00'

        begin_row_number = 0
        begin_col_number = 1
        color = "red"
        file_name = os.path.join(sub_path, "股票收益分解_" + cal_type + fund_name + date + ".xlsx")
        sheet_name = fund_name

        excel = WriteExcel(file_name)
        worksheet = excel.add_worksheet(sheet_name)
        excel.write_pandas(all_data, worksheet, begin_row_number=begin_row_number, begin_col_number=begin_col_number,
                           num_format_pd=num_format_pd, color=color, fillna=True)
        excel.close()
        print('The Stock Return And Asset Of Fund %s At Date %s Saved ' % (fund_name, date))
        return stock_return, mg_fee, trade_fee, stock_asset
        ################################################################################################################
    else:
        print('The Stock Return And Asset Of Fund %s At Date %s is Zero ' % (fund_name, date))
        return 0, mg_fee, trade_fee, 0

if __name__ == '__main__':

    fund_name = '泰达中证500指数分级'
    beg_date = '20170101'
    end_date = datetime.today()
    path = 'C:\\Users\\doufucheng\\OneDrive\\Desktop\\data\\'
    close_unadjust = Stock().get_factor_h5("Price_Unadjust", None, "primary_mfc")
    adjust_factor = Stock().get_factor_h5("AdjustFactor", None, "primary_mfc")
    mg_fee_ratio = 0.015 + 0.0025
    date_series = Date().get_trade_date_series(beg_date, end_date)

    for date in date_series:
        print(CalStockReturnDaily(fund_name, date, path, close_unadjust, adjust_factor, mg_fee_ratio, cal_type="close"))
        print(CalStockReturnDaily(fund_name, date, path, close_unadjust, adjust_factor, mg_fee_ratio, cal_type="average"))

