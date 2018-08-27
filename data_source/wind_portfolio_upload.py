import pandas as pd
from quant.stock.stock import Stock
from quant.stock.date import Date
from WindPy import w
w.start()


def upload_weight_date(port_name, change_date, data_pd, owner = "W6964909132"):

    """
    上传wind组合权重
    """

    type = "weight"

    code_str = ','.join(list(data_pd.Code.values))
    weight_str = ','.join(list(data_pd.Weight.values))
    price_str = ','.join(list(data_pd.Price.values))

    direction_str = ','.join(list(data_pd.Direction.values))
    credit_str = ','.join(list(data_pd.CreditTrading.values))

    res = w.wupf(port_name, change_date, code_str, weight_str, price_str,
           "Direction=%s;CreditTrading=%s;Owner=%s;type=%s" % (direction_str, credit_str, owner, type))

    if res.ErrorCode == 0:
        print("################### Uploading %s At %s is OK ###################" % (port_name, change_date))
    else:
        print("################### Uploading %s At %s is Error ###################" % (port_name, change_date))


def upload_weight_period(port_name, owner, data_pd, status_adjust = True, date_adjust = True):

    # owner = "W6964909132"
    # port_name = "A股多因子"

    # status_adjust = True  # 剔除停牌、涨跌停股票，并重新调整权重
    # date_adjust = True  # 本个交易日买入 还是下个交易日买入
    #
    # data_pd = pd.DataFrame([["20170808", "000001.SZ", '0.20', '0.0', 'Long', 'No'],
    #                         ["20170808", '000002.SZ', '0.30', '0.0', 'Long', 'No'],
    #                         ["20170808", '000004.SZ', '0.20', '0.0', 'Long', 'No'],
    #                         ["20170808", '601330.SH', '0.10', '0.0', 'Long', 'No'],
    #                         ["20180101", "000001.SZ", '0.40', '0.0', 'Long', 'No'],
    #                         ["20180101", '000002.SZ', '0.20', '0.0', 'Long', 'No'],
    #                         ["20180101", '600000.SH', '0.20', '0.0', 'Long', 'No'],
    #                         ["20180101", '601330.SH', '0.20', '0.0', 'Long', 'No'],
    #                         ], columns=['Date', 'Code', 'Weight', 'Price', 'Direction', 'CreditTrading'])

    date_set = list(set(data_pd['Date'].values))
    code_set = list(set(data_pd['Code'].values))
    date_set.sort()
    code_set.sort()

    adjust_cash_date = Date().get_trade_date_offset(date_set[0], -1)
    res = w.wupf(port_name, adjust_cash_date, "CNY", "100000000", "1",
                 "Owner=%s;Direction=Long;CreditTrading=No;HedgeType=Spec;" % owner)
    if res.ErrorCode == 0:
        print("############ Uploading Cash %s At %s is OK ############" % (port_name, adjust_cash_date))
    else:
        print("############ Uploading Cash %s At %s is Error ############" % (port_name, adjust_cash_date))

    if date_adjust:
        data_pd.Date = data_pd.Date.map(lambda x: Date().get_trade_date_offset(x, 1))
    else:
        data_pd.Date = data_pd.Date.map(lambda x: Date().get_trade_date_offset(x, 0))

    date_set = list(set(data_pd['Date'].values))
    code_set = list(set(data_pd['Code'].values))
    date_set.sort()
    code_set.sort()

    if status_adjust:

        status = Stock().get_h5_primary_factor("TradingStatus", None, date_set, code_set)
        data_pd.Weight = data_pd.Weight.map(float)

        for i_date in range(0, len(date_set)):
            date = date_set[i_date]
            data_pd_date = data_pd[data_pd.Date == date]

            trade_stock_list = set(status[status[date] == 0.0].index)
            trade_stock_list = list(set(trade_stock_list) & set(data_pd_date.Code))
            data_pd_date_filter = data_pd_date[data_pd_date.Code.map(lambda x: x in trade_stock_list)]
            if data_pd_date.Weight.sum() > 1.0:
                print("################### The sum of weight %s At %s  is bigger than 100 ###################" % (port_name, date))
            weight_adjust = data_pd_date.Weight.sum() / data_pd_date_filter.Weight.sum()
            data_pd_date_filter.Weight *= weight_adjust
            print(data_pd_date_filter.Weight.sum())

            if i_date == 0:
                data_pd_new = data_pd_date_filter
            else:
                data_pd_new = pd.concat([data_pd_new, data_pd_date_filter], axis=0)

    data_pd_new.reset_index(drop=True)
    data_pd = data_pd_new
    data_pd.Weight = data_pd.Weight.map(str)

    for i_date in range(0, len(date_set)):

        date = date_set[i_date]
        data_pd_date = data_pd[data_pd.Date == date]

        col = ['Code', 'Weight', 'Price', 'Direction', 'CreditTrading']

        data_pd_date = data_pd_date[col]
        print(data_pd_date)
        upload_weight_date(port_name, date, data_pd_date, owner)


if __name__ == "__main__":

    owner = "W6964909132"
    port_name = "东方红产业升级"

    status_adjust = True  # 剔除停牌、涨跌停股票，并重新调整权重
    date_adjust = True  # 本个交易日买入 还是下个交易日买入

    # data_pd = pd.DataFrame([["20170808", "000001.SZ", '0.20', '0.0', 'Long', 'No'],
    #                         ["20170808", '000002.SZ', '0.30', '0.0', 'Long', 'No'],
    #                         ["20170808", '000004.SZ', '0.20', '0.0', 'Long', 'No'],
    #                         ["20170808", '601330.SH', '0.10', '0.0', 'Long', 'No'],
    #                         ["20180101", "000001.SZ", '0.40', '0.0', 'Long', 'No'],
    #                         ["20180101", '000002.SZ', '0.20', '0.0', 'Long', 'No'],
    #                         ["20180101", '600000.SH', '0.20', '0.0', 'Long', 'No'],
    #                         ["20180101", '601330.SH', '0.20', '0.0', 'Long', 'No'],
    #                         ], columns=['Date', 'Code', 'Weight', 'Price', 'Direction', 'CreditTrading'])

    file = 'E:\\3_数据\\4_fund_data\\4_fund_holding_predict\ols_stock_weight\\最后预测持仓权重_000619.OF_AllDate.csv'
    data_pd = pd.read_csv(file, index_col=[0], encoding='gbk')
    data_pd /= 100

    for i_date in range(len(data_pd.columns)):

        date = data_pd.columns[i_date]
        data_pd_date = data_pd[date]
        data_pd_date = data_pd_date.dropna()

        result_add = pd.DataFrame(data_pd_date.values, index=data_pd_date.index, columns=['Weight'])
        result_add = result_add[result_add['Weight'] > 0.0]
        result_add['Weight'] = result_add['Weight'] / result_add['Weight'].sum() * 0.94
        result_add['Code'] = result_add.index
        result_add['Date'] = date
        result_add['Price'] = "0.0"
        result_add['Direction'] = "Long"
        result_add['CreditTrading'] = 'No'
        if i_date == 0:
            result = result_add
        else:
            result = pd.concat([result, result_add], axis=0)

    result.reset_index(drop=True)
    upload_weight_period(port_name, owner, result, status_adjust=True, date_adjust=True)
