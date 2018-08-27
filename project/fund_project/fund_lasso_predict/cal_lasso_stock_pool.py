import pandas as pd
from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.fund.fund import Fund
from datetime import datetime
from sklearn.linear_model import Lasso


def cal_lasso_stock_pool(s_marketvalue, f_pct, s_pct,
                         beg_date, end_date, fund_code, out_path, period_min=40):

    """
    利用最近一段时间基金净值和股票收益率 Lasso回归出股票池 控制股票数量在20只附近
    """

    # 参数
    ################################################################################
    trade_beg_date = Date().change_to_str(beg_date)
    trade_end_date = Date().change_to_str(end_date)

    s_marketvalue = pd.DataFrame(s_marketvalue[trade_end_date].values, index=s_marketvalue.index,
                                 columns=[trade_end_date])
    s_marketvalue = s_marketvalue.sort_values(by=[trade_end_date], ascending=False)
    s_marketvalue = s_marketvalue.dropna()
    s_marketvalue = s_marketvalue.ix[0:int(0.65*len(s_marketvalue)), :]
    stock_pool = list(s_marketvalue.index)

    date_series = Date().get_trade_date_series(trade_beg_date, trade_end_date)
    f_pct = f_pct.ix[date_series, fund_code]
    s_pct = s_pct.ix[date_series, stock_pool]
    s_pct = s_pct.dropna(how='all')
    f_pct = f_pct.dropna()

    data = pd.concat([f_pct, s_pct], axis=1)
    data = data.ix[beg_date:end_date, :]
    data = data.dropna(how='all')
    data = data.fillna(0.0)
    y = data[fund_code].values
    x = data.iloc[:, 1:].values

    def lasso_regression(x, y, trade_end_date, alpha=0.50):

        model = Lasso(alpha=alpha, fit_intercept=False)
        model.fit(x, y)

        res = pd.DataFrame(model.coef_[model.coef_ > 0.001],
                           index=s_pct.columns[model.coef_ > 0.001], columns=[trade_end_date])
        res = res.sort_values(by=[trade_end_date], ascending=False)
        return res

    if len(data) > period_min and len(f_pct) > period_min:

        l, alpha = 50, 0.50

        while l > 25:
            res = lasso_regression(x, y, trade_end_date, alpha)
            alpha *= 1.1
            l = len(res)

        print("%s AT %s TO %s Data Len is %s" % (fund_code, trade_beg_date, trade_end_date, len(data)))
        print("LASSO回归股票池的个数: %s, 权重绝对值之和为 %s" % (len(res), res.abs().sum()))
        res.to_csv(out_path + 'LASSO回归股票池_' + fund_code + "_" + trade_end_date + '.csv')
    else:
        print("%s AT %s TO %s Data Len is %s" % (fund_code, trade_beg_date, trade_end_date, len(data)))
        res = pd.DataFrame([])
    return res


def cal_lasso_stock_pool_all():

    lasso_period = 60
    lasso_period_min = 40
    beg_date = "20041231"
    end_date = datetime.today()
    out_path = "E:\\3_数据\\4_fund_data\\4_fund_holding_predict\\lasso_stock_pool\\"

    quarter_date = Date().get_last_fund_quarter_date(end_date)
    quarter_date = '20180630'
    date_series = Date().get_trade_date_series(beg_date, end_date, period="M")
    fund_pool = Fund().get_fund_pool_code(quarter_date, "优质基金池")

    s_marketvalue = Stock().get_h5_primary_factor("Mkt_freeshares", date_list=None)
    f_pct = Fund().get_fund_factor("Repair_Nav_Pct", date_list=None, fund_pool=fund_pool)
    s_pct = Stock().get_h5_primary_factor("Pct_chg", date_list=None, stock_pool=None).T

    for i_fund in range(0, len(fund_pool)):

        fund_code = fund_pool[i_fund]

        for i_date in range(0, len(date_series)):

            period_end_date = date_series[i_date]
            period_beg_date = Date().get_trade_date_offset(period_end_date, -lasso_period)
            res_add = cal_lasso_stock_pool(s_marketvalue, f_pct, s_pct,
                                           period_beg_date, period_end_date, fund_code, out_path, lasso_period_min)

            if i_date == 0:
                res = res_add
            else:
                res = pd.concat([res, res_add], axis=1)
            print(res)

        res.to_csv(out_path + 'LASSO回归股票池_' + fund_code + "_AllDate.csv")


def get_lasso_stock_pool(end_date, fund_code):

    out_path = "E:\\3_数据\\4_fund_data\\4_fund_holding_predict\\lasso_stock_pool\\"
    trade_end_date = Date().get_trade_date_offset(end_date, 0)
    try:
        file = out_path + 'LASSO回归股票池_' + fund_code + "_" + trade_end_date + '.csv'
        data = pd.read_csv(file, encoding='gbk', index_col=[0])
    except:
        data = pd.DataFrame([])
    return data

if __name__ == "__main__":

    cal_lasso_stock_pool_all()

