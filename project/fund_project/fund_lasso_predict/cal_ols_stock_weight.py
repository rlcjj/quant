import pandas as pd
from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.fund.fund import Fund
from quant.stock.barra import Barra
from datetime import datetime
from quant.project.fund_project.fund_lasso_predict.cal_lasso_stock_pool import get_lasso_stock_pool
import numpy as np
from cvxopt import matrix
import cvxopt.solvers as sol


def cal_ols_stock_weight(f_pct, s_pct, last_fund_holding, position_all,
                         beg_date, end_date, fund_code, out_path):

    # beg_date = "20170930"
    # end_date = "20171231"
    # fund_code = "000001.OF"
    # out_path = "E:\\3_数据\\4_fund_data\\4_fund_holding_predict\\predict_E1\\"

    # 参数
    #######################################################################################
    up_fund_ratio = 0.3
    down_fund_ratio = 0.5
    up_fund_limit = 0.03
    down_fund_limit = 0.02
    style_std = 0.30

    beg_date = Date().change_to_str(beg_date)
    end_date = Date().change_to_str(end_date)

    # 收益率数据
    #######################################################################################
    date_series = Date().get_trade_date_series(beg_date, end_date)
    f_pct = f_pct.ix[date_series, fund_code]
    s_pct = s_pct.ix[date_series, :]

    # 风格暴露
    #######################################################################################
    # f_exp = Fund().get_fund_regression_exposure_date(fund_code, date_series[-1])

    # 股票池数据
    #######################################################################################
    lasso_stock_weight = get_lasso_stock_pool(end_date, fund_code)
    lasso_stock_pool = list(lasso_stock_weight.index)

    quarter_date = Date().get_last_fund_quarter_date(end_date)
    last_fund_holding = last_fund_holding[last_fund_holding.Date == quarter_date]
    last_fund_holding = last_fund_holding[last_fund_holding.FundCode == fund_code]
    last_fund_holding.index = last_fund_holding.StockCode
    last_fund_holding['Weight'] /= 100.0

    # 有效数据大于0 开始计算
    #######################################################################################
    if len(last_fund_holding) > 0 and len(lasso_stock_pool) > 0:

        last_fund_pool = list(last_fund_holding.index[0:10])

        stock_list = list(set(lasso_stock_pool) | set(last_fund_pool))
        s_pct = s_pct.ix[:, stock_list]

        # 股票上下限数据
        #######################################################################################
        position = position_all.ix[quarter_date, fund_code] / 100.0
        if np.isnan(position):
            position = 0.80
        # position = np.nanmean([position, f_exp.ix["CTY", :].values[0]])

        # old_fund_up = min(1.2*last_fund_holding.ix[0, 'Weight'], 0.09)  # 有些持仓很分散的股票的上限要小
        # new_fund_up = min(old_fund_up*0.5, 0.035)   # 限制新进股票的最高上限、这里限制的比较严格是因为新近股票就是风险
        # print("old_fund_up", old_fund_up, "new_fund_up", new_fund_up)

        fund_weight = pd.concat([last_fund_holding.ix[0:10, 'Weight'], lasso_stock_weight], axis=1)
        fund_weight.columns = ['Last_Weight', 'Lasso_Weight']
        fund_weight['Weight'] = fund_weight.max(axis=1)

        fund_weight['Weight'] = fund_weight['Weight'] / fund_weight['Weight'].sum() * position
        fund_weight['Type'] = fund_weight['Last_Weight'].map(lambda x: "New_Stock" if np.isnan(x) else "Old_Stock")

        fund_weight['Weight_up'] = fund_weight['Weight'].map(
            lambda x: min(max(x * (1 + up_fund_ratio), x + up_fund_limit), 0.15))
        fund_weight['Weight_down'] = fund_weight['Weight'].map(
            lambda x: max(min(x * (1 - down_fund_ratio), x - down_fund_limit), 0))

        print(fund_weight[['Weight', 'Weight_up', 'Weight_down']] * 100)
        data = pd.concat([f_pct, s_pct], axis=1)
        data = data.ix[beg_date:end_date, :]
        data = data.dropna(how='all')
        data = data.fillna(0.0)

        # 风格约束
        ################################################################
        # end_date = date_series[-1]
        # beg_date = Date().get_trade_date_offset(end_date, -60)
        # s_exp = Barra().get_factor_exposure_average(beg_date, end_date, type_list=['STYLE']).T
        # s_exp = s_exp[stock_list]
        # exp = pd.concat([f_exp, s_exp], axis=1)
        # exp = exp.dropna(how='all')
        # exp = exp.fillna(0.0)
        # y_exp = np.row_stack(exp[fund_code].values)
        # x_exp = exp.iloc[:, 1:].values
        # y_exp_up = y_exp + style_std
        # y_exp_low = y_exp - style_std
        # style_limit = np.row_stack((y_exp_up, -y_exp_low))
        # A = np.row_stack((x_exp, -x_exp))

        # 最小化函数
        ##################################################################
        y = data[fund_code].values
        X = data.iloc[:, 1:].values
        P = 2 * np.dot(np.transpose(X), X)
        Q = -2 * np.dot(np.transpose(X), y)

        # 单个股票权重上下限约束
        ################################################################
        G_up = np.diag(np.ones(len(stock_list)))
        G_low = - np.diag(np.ones(len(stock_list)))
        G = np.row_stack((G_up, G_low))

        h_up = np.vstack(fund_weight['Weight_up'].values)
        h_low = -np.vstack(fund_weight['Weight_down'].values)
        h = np.row_stack((h_up, h_low))

        # 总权重上下限约束
        ################################################################
        G_p_up = np.ones(len(stock_list)).reshape(1, len(stock_list))
        G_p_low = - np.ones(len(stock_list)).reshape(1, len(stock_list))
        G_p = np.row_stack((G_p_up, G_p_low))
        G = np.row_stack((G, G_p))

        h_p_up = [[min(position + 0.05, 0.95)]]
        h_p_low = [[-min(max(position - 0.05, 0.65), h_p_up[0][0])]]

        print("正在计算 %s 在 %s 的股票持仓权重 " % (fund_code, end_date))
        print("基金约束上下限制为 %s %s" % (h_p_low, h_p_up))
        print("基金约束限制矩阵大小为 %s %s" % (G.shape, h.shape))
        h_p = np.row_stack((h_p_up, h_p_low))
        h = np.row_stack((h, h_p))

        # G = np.row_stack((G, A))
        # h = np.row_stack((h, style_limit))

        # 优化求解
        ##################################################################

        P = matrix(P)
        Q = matrix(Q)
        G = matrix(G)
        h = matrix(h)

        model = sol.qp(P, Q, G, h)

        # 输出结果
        ##################################################################
        weight = list(model['x'][:])
        res = pd.DataFrame(weight, index=stock_list, columns=[end_date])
        res = res[res[end_date] > 0.0001]
        res = res.sort_values(by=[end_date], ascending=False)
        res[end_date] *= 100

        print("基金仓位为%s 最后预测持仓权重个数%s", res[end_date].sum(), len(res))

        if model['status'] == 'optimal':
            print("二次规划成功，最终结果 %s %s " %(fund_code, end_date))
            res.to_csv(out_path + '最后预测持仓权重_' + fund_code + '_' + end_date + '.csv')
            return res
        else:
            print("二次规划异常，没有最终结果 %s %s " %(fund_code, end_date))
            return pd.DataFrame([])
    else:
        print("%s 在 %s 的数据长度为0 " % (fund_code, end_date))
        return pd.DataFrame([])


def cal_ols_stock_weight_all():

    lasso_period = 60
    beg_date = "20041231"
    end_date = datetime.today()
    out_path = "E:\\3_数据\\4_fund_data\\4_fund_holding_predict\\ols_stock_weight\\"

    quarter_date = Date().get_last_fund_quarter_date(end_date)
    quarter_date = '20180630'
    date_series = Date().get_trade_date_series(beg_date, end_date, period="M")
    fund_pool = Fund().get_fund_pool_code(quarter_date, "优质基金池")

    f_pct = Fund().get_fund_factor("Repair_Nav_Pct", date_list=None, fund_pool=fund_pool)
    s_pct = Stock().get_h5_primary_factor("Pct_chg", date_list=None, stock_pool=None).T
    last_fund_holding = Fund().get_fund_holding_all()
    position_all = Fund().get_fund_factor("Stock_Ratio", None, None)

    for i_fund in range(0, len(fund_pool)):

        fund_code = fund_pool[i_fund]

        for i_date in range(0, len(date_series)):

            period_end_date = date_series[i_date]
            period_beg_date = Date().get_trade_date_offset(period_end_date, -lasso_period)
            res_add = cal_ols_stock_weight(f_pct, s_pct, last_fund_holding, position_all,
                                           period_beg_date, period_end_date, fund_code, out_path)

            if i_date == 0:
                res = res_add
            else:
                res = pd.concat([res, res_add], axis=1)

        res.to_csv(out_path + '最后预测持仓权重_' + fund_code + "_AllDate.csv")
        print(res)


def get_ols_stock_weight_all_date(fund_code):

    out_path = "E:\\3_数据\\4_fund_data\\4_fund_holding_predict\\ols_stock_weight\\"
    try:
        data = pd.read_csv(out_path + '最后预测持仓权重_' + fund_code + "_AllDate.csv", index_col=[0], encoding='gbk')
    except:
        data = pd.DataFrame([])

    return data

if __name__ == "__main__":

    cal_ols_stock_weight_all()
