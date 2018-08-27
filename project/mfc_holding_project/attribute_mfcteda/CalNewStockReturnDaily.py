from quant.mfc.mfc_data import MfcData
from quant.stock.date import Date
from quant.stock.stock import Stock
from quant.utility_fun.code_format import stock_code_add_postfix
import pandas as pd
import numpy as np
from datetime import datetime
import os
from quant.utility_fun.write_excel import WriteExcel


def CalNewStockReturnDaily(fund_name, date, path,
                           close_unadjust, adjust_factor, cal_type="close"):

    """
    计算当日基金资产中有多少钱是新股波动带来的
    有两种 计算方式
    1、新股以当日收盘价卖出(close)  或者继续当日持有 新股收益 = 昨日收盘数量 * 当日收盘价格
    2、新股以当日均价卖出(average)  或者继续当日持有
    """

    # 前一个交易日
    ##########################################################################################
    pre_date = Date().get_trade_date_offset(date, -1)

    # 读取持仓数据
    ##########################################################################################
    try:
        security = MfcData().get_fund_security(date)
        security_pre_date = MfcData().get_fund_security(pre_date)

        # 如果用均价计算 还要读取 交易持仓信息
        ##########################################################################################
        if cal_type == "average":
            try:
                trade = MfcData().get_trade_statement(date)
            except:
                print('The Trading Data For New Stock Return Of Fund %s At Date %s is Null ' % (fund_name, date))
        ##########################################################################################
    except:
        print('The Holding Data For New Stock Return Of Fund %s At Date %s is Null ' % (fund_name, date))
        return np.nan, np.nan

    # 读取价格数据
    ##########################################################################################
    try:
        close_unadjust_date = close_unadjust[date]
        close_unadjust_pre_date = close_unadjust[pre_date]
        adjust_factor_date = adjust_factor[date]
        adjust_factor_pre_date = adjust_factor[pre_date]
        ipo = Stock().get_ipo_date()
    except:
        print('The Price Data For New Stock Return Of Fund %s At Date %s is Null ' % (fund_name, date))
        return np.nan, np.nan

    # 整理 持仓数据 交易数据
    ##########################################################################################

    # 整理当日股票持仓
    ##########################################################################################
    security_data = security[security['基金名称'] == fund_name]
    security_data = security_data[security_data['证券类别'] == '股票']
    security_data = security_data[['基金名称', '证券名称', '持仓', '证券代码']]
    security_data['证券代码'] = security_data['证券代码'].map(stock_code_add_postfix)
    security_data.index = security_data['证券代码'].values
    security_data = security_data[['证券名称', '持仓']]
    security_data.columns = ['CodeName', 'TodayVol']

    # 整理前日股票持仓
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

    if cal_type == 'average':

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

        #  合并数据
        ##########################################################################################
        holding = pd.concat([security_data, trade_data, security_pre_date_data], axis=1)
        all_data = pd.concat([holding, close_2_days], axis=1)
        all_data = pd.concat([all_data, ipo['IPO_DATE']], axis=1)

        all_data = all_data.dropna(subset=['TodayVol'])

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
        ipo_date = Date().get_trade_date_offset(date, -40)
        all_data = all_data[all_data['IPO_DATE'] <= date]
        all_data = all_data[all_data['IPO_DATE'] >= ipo_date]

    else:
        #  合并数据
        ##########################################################################################
        holding = pd.concat([security_pre_date_data, security_data], axis=1)
        all_data = pd.concat([holding, close_2_days], axis=1)
        all_data = pd.concat([all_data, ipo['IPO_DATE']], axis=1)

        # 整理计算 当日新股收盘资产 和 假设今日收盘交易 新股的收益
        ##########################################################################################
        all_data = all_data.dropna(subset=['YestodayVol'])
        price_change = all_data['Close'] - all_data['PreClose'] / all_data['AdjustFactor']
        all_data['StockReturn'] = all_data['YestodayVol'] * price_change

        all_data = all_data.dropna(subset=['StockReturn'])
        ipo_date = Date().get_trade_date_offset(date, -40)
        all_data = all_data[all_data['IPO_DATE'] <= date]
        all_data = all_data[all_data['IPO_DATE'] >= ipo_date]

    if len(all_data) > 0:

        # 今日新股计算详细数据 存储到文件中
        ################################################################################################################
        stock_return = all_data['StockReturn'].sum()
        stock_asset = (all_data['Close'] * all_data['TodayVol']).sum()
        sub_path = os.path.join(path, fund_name, '新股')
        if not os.path.exists(sub_path):
            os.makedirs(sub_path)

        num_format_pd = pd.DataFrame([], columns=all_data.columns, index=['format'])
        num_format_pd.ix['format', :] = '0.00'

        begin_row_number = 0
        begin_col_number = 1
        color = "red"
        file_name = os.path.join(sub_path, "新股收益分解_" + cal_type + fund_name + date + ".xlsx")
        sheet_name = fund_name

        excel = WriteExcel(file_name)
        worksheet = excel.add_worksheet(sheet_name)
        excel.write_pandas(all_data, worksheet, begin_row_number=begin_row_number, begin_col_number=begin_col_number,
                           num_format_pd=num_format_pd, color=color, fillna=True)
        excel.close()
        print('The New Stock Return And Asset Of Fund %s At Date %s Saved ' % (fund_name, date))
        return stock_return, stock_asset
        ################################################################################################################
    else:
        print('The New Stock Return And Asset Of Fund %s At Date %s is Zero ' % (fund_name, date))
        return 0, 0

if __name__ == '__main__':

    fund_name = '泰达中证500指数分级'
    beg_date = '20170210'
    end_date = datetime.today()
    path = 'C:\\Users\\doufucheng\\OneDrive\\Desktop\\data\\'

    close_unadjust = Stock().get_factor_h5("Price_Unadjust", None, "primary_mfc")
    adjust_factor = Stock().get_factor_h5("AdjustFactor", None, "primary_mfc")

    date_series = Date().get_trade_date_series(beg_date, end_date)

    for date in date_series:

        print(CalNewStockReturnDaily(fund_name, date, path, close_unadjust, adjust_factor, cal_type="close"))
        print(CalNewStockReturnDaily(fund_name, date, path, close_unadjust, adjust_factor, cal_type="average"))


