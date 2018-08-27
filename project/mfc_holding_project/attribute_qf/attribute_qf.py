from quant.mfc.mfc_data import MfcData
from quant.stock.date import Date
from quant.utility_fun.code_format import stock_code_add_postfix
from datetime import datetime
import pandas as pd
import os


def get_mfcteda_holding_data():

    fund_name = '泰达宏利启富'
    beg_date = '20180625'
    end_date = datetime.today().strftime('%Y%m%d')
    end_date = '20180731'

    date_series = Date().get_trade_date_series(beg_date, end_date)
    result = pd.DataFrame([], index=date_series, columns=['产品单位净值', '当日净资产(万元)', '股票仓位', '当日股票贡献(万元)'])

    for i in range(len(date_series)):

        date = date_series[i]

        print(date)
        try:
            asset = MfcData().get_fund_asset(date)
            asset.index = asset['基金名称']

            trade = MfcData().get_trade_statement(date)
            trade = trade[trade['基金名称'] == fund_name]
            trade = trade[trade['资产类别'] == '股票资产']
            trade = trade[['基金名称', '证券名称', '成交数量', '市场成交均价', '委托方向', '证券代码']]
            trade['证券代码'] = trade['证券代码'].map(stock_code_add_postfix)
            trade.index = trade['证券代码']
            # if len(trade) > 0:
            #     print(i, date, len(trade))

            security = MfcData().get_fund_security(date)
            security = security[security['基金名称'] == fund_name]
            security = security[security['证券类别'] == '股票']
            security = security[['基金名称', '证券名称', '持仓', '市均价', '最新价', '证券代码']]
            security['证券代码'] = security['证券代码'].map(stock_code_add_postfix)
            security = security.reset_index(drop=True)

            result.ix[date, "产品单位净值"] = asset.ix[fund_name, '单位净值']
            result.ix[date, "当日净资产(万元)"] = asset.ix[fund_name, '净值'] / 10000.0
            result.ix[date, '股票仓位'] = asset.ix[fund_name, '股票资产/净值(%)']
            result.ix[date, '债券资产'] = asset.ix[fund_name, '债券资产'] / 10000.0
            result.ix[date, '股票资产'] = asset.ix[fund_name, '股票资产'] / 10000.0
            result.ix[date, '当前现金余额'] = asset.ix[fund_name, '当前现金余额'] / 10000.0
            result.ix[date, '回购资产'] = asset.ix[fund_name, '回购资产'] / 10000.0


            # price = pd.DataFrame(security[['证券名称', '持仓']].values,
            #                      index=security['证券代码'].values, columns=['Name', 'Total_Vol'])
            #
            # trade_price = pd.DataFrame(trade[['成交数量', '市场成交均价', '委托方向']].values,
            #                            index=trade.index, columns=['Trade_Vol', 'Trade_Price', 'SellOrBuy'])
            # data = pd.concat([price, trade_price], axis=1)
            #
            # from WindPy import w
            # w.start()
            # price_wind = w.wss(','.join(list(data.index)), "close,pre_close", "tradeDate=" + date + ";priceAdj=U;cycle=D")
            # price_wind_pd = pd.DataFrame(price_wind.Data, columns=price_wind.Codes, index=['Close', 'Pre_Close']).T

            # all_data = pd.concat([data, price_wind_pd], axis=1)
            # all_data[['Trade_Vol', 'Total_Vol']] = all_data[['Trade_Vol', 'Total_Vol']].fillna(0.0)
            # all_data['Hold_Vol'] = all_data['Total_Vol'] - all_data['Trade_Vol']
            # all_data['Hold_Return'] = all_data['Hold_Vol'] * (all_data['Close'] - all_data['Pre_Close'])
            # buy_code_list = list(all_data[all_data['SellOrBuy'] == "买入"].index)
            # sell_code_list = list(all_data[all_data['SellOrBuy'] == "卖出"].index)
            #
            # all_data.ix[buy_code_list, "Buy_Return"] = all_data.ix[buy_code_list, 'Trade_Vol'] * \
            # (all_data.ix[buy_code_list, 'Close'] - all_data.ix[buy_code_list, 'Trade_Price'])
            # all_data.ix[sell_code_list, "Sell_Return"] = all_data.ix[buy_code_list, 'Trade_Vol'] * \
            # (all_data.ix[buy_code_list, 'Trade_Price'] - all_data.ix[buy_code_list, 'Pre_Close'])
            #
            # today_return = all_data.sum()[['Buy_Return', 'Sell_Return', 'Hold_Return']].sum()
            # result.ix[date, '当日股票贡献(万元)'] = today_return / 10000.0

        except:
            pass

    result.to_csv("qf.csv")


if __name__ == '__main__':

    get_mfcteda_holding_data()
