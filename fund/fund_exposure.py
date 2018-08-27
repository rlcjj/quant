from datetime import datetime
import os
import pandas as pd
import cvxopt.solvers as sol
from cvxopt import matrix
import statsmodels.api as sm
import numpy as np
from quant.fund.fund_pool import FundPool
from quant.fund.fund_holder import FundHolder
from quant.fund.fund_factor import FundFactor
from quant.stock.barra import Barra
from quant.stock.date import Date
from quant.param.param import Parameter
from quant.utility_fun.pandas_fun import pandas_add_row


class FundHolderExposure(object):

    """
    利用年度和半年度持仓信息计算当时基金的BARRA因子暴露

    cal_fund_holder_exposure()
    cal_fund_holder_exposure_all()
    get_fund_holder_exposure()

    """

    def __init__(self):

        self.holder_exposure_name = 'Fund_Holder_Exposure'

    def cal_fund_holder_exposure(self, fund, beg_date, end_date):

        # 每半年计算一次
        type_list = ['STYLE', 'COUNTRY', 'INDUSTRY']
        date_series = Date().get_normal_date_series(beg_date, end_date, period='S')

        for i_date in range(len(date_series)):

            date = date_series[i_date]
            report_date = Date().get_normal_date_month_end_day(date)
            trade_date = Date().get_trade_date_month_end_day(date)

            barra_name = list(Barra().get_factor_name(type_list)['NAME_EN'].values)
            barra_exposure = Barra().get_factor_exposure_date(trade_date, type_list)
            fund_holding = FundHolder().get_fund_holding_report_date_fund(fund, report_date)
            print("########## Calculate Holder Exposure %s %s ##########" % (fund, report_date))

            if (barra_exposure is None) or (fund_holding is None):
                exposure_add = pd.DataFrame([], columns=barra_name, index=[report_date])
            else:
                fund_holding = fund_holding['Weight']
                data = pd.concat([fund_holding, barra_exposure], axis=1)
                data = data.dropna()

                if (len(data) == 0) or (data is None):
                    exposure_add = pd.DataFrame([], columns=barra_name, index=[report_date])
                else:
                    exposure_add = pd.DataFrame([], columns=barra_name, index=[report_date])

                    for i_factor in range(len(barra_name)):
                        factor_name = barra_name[i_factor]
                        data_weight = data[['Weight', factor_name]]
                        data_weight['StockExposure'] = data['Weight'] * data[factor_name]
                        exposure_add.ix[report_date, factor_name] = data_weight['StockExposure'].sum() / 100.0

            if i_date == 0:
                exposure_new = exposure_add
            else:
                exposure_new = pd.concat([exposure_new, exposure_add], axis=0)

        # 合并新数据
        ####################################################################
        out_path = Parameter().get_read_file(self.holder_exposure_name)
        out_file = os.path.join(out_path, 'Fund_Holder_Exposure_' + fund + '.csv')

        if os.path.exists(out_file):
            exposure_old = pd.read_csv(out_file, index_col=[0], encoding='gbk')
            exposure_old.index = exposure_old.index.map(str)
            params = pandas_add_row(exposure_old, exposure_new)
        else:
            params = exposure_new
        params.to_csv(out_file)

    def cal_fund_holder_exposure_all(self, beg_date="19991231", end_date=datetime.today(), fund_pool="基金持仓基准基金池"):

        quarter_date = Date().get_last_fund_quarter_date(end_date)
        fund_pool = FundPool().get_fund_pool_code(quarter_date, fund_pool)

        for i_fund in range(0, len(fund_pool)):
            fund_code = fund_pool[i_fund]
            self.cal_fund_holder_exposure(fund_code, beg_date, end_date)

    def get_fund_holder_exposure(self, fund, type_list=["STYLE"]):

        out_path = Parameter().get_read_file(self.holder_exposure_name)
        out_file = os.path.join(out_path, 'Fund_Holder_Exposure_' + fund + '.csv')
        exposure = pd.read_csv(out_file, index_col=[0], encoding='gbk')
        exposure.index = exposure.index.map(str)

        factor_name = Barra().get_factor_name(type_list=type_list)
        factor_name = list(factor_name["NAME_EN"].values)
        exposure = exposure[factor_name]
        return exposure

    def get_fund_holder_exposure_date(self, fund, date, type_list=["STYLE"]):

        date = Date().get_normal_date_month_end_day(date)
        exposure = self.get_fund_holder_exposure(fund, type_list)
        exposure_date = exposure.ix[date, :]
        exposure_date = pd.DataFrame(exposure_date.values, index=exposure_date.index, columns=[fund]).T
        return exposure_date


class FundRegressionExposure(object):

    """
    利用有约束的线性回归的方法推测当前基金的Barra风格暴露

    将回归转化成为二次规划：限制基金的仓位上下限 和风格暴露上下限

    cal_fund_regression_exposure()
    cal_fund_regression_exposure_all()
    get_fund_regression_exposure()
    """

    def __init__(self):

        self.regression_exposure_name = 'Fund_Regression_Exposure'
        self.regression_period = 60
        self.regression_period_min = 40

    def cal_fund_regression_exposure(self, fund, beg_date, end_date, period="M"):

        # 参数
        ####################################################################
        up_style_exposure = 1.5
        up_position_exposure = 0.95
        low_position_exposure = 0.75
        position_sub = 0.10

        beg_date = Date().change_to_str(beg_date)
        end_date = Date().change_to_str(end_date)

        # 取得数据
        ####################################################################
        type_list = ['STYLE', 'COUNTRY']

        barra_name = list(Barra().get_factor_name(type_list)['NAME_EN'].values)
        barra_return = Barra().get_factor_return(None, None, type_list)

        date_series = Date().get_trade_date_series(beg_date, end_date, period=period)
        fund_return = FundFactor().get_fund_factor("Repair_Nav_Pct", None, [fund])

        data = pd.concat([fund_return, barra_return], axis=1)
        data = data.dropna()
        print(" Fund Code Total Len %s " % len(data))
        factor_number = len(barra_name)

        # 循环回归计算每天的暴露
        ####################################################################

        for i_date in range(0, len(date_series)):

            period_end_date = date_series[i_date]
            period_beg_date = Date().get_trade_date_offset(period_end_date, -self.regression_period)

            period_date_series = Date().get_trade_date_series(period_beg_date, period_end_date)
            data_periods = data.ix[period_date_series, :]
            data_periods = data_periods.dropna()

            quarter_date = Date().get_last_fund_quarter_date(period_end_date)
            stock_ratio = (FundFactor().get_fund_factor("Stock_Ratio", [quarter_date], [fund]) / 100).values[0][0]
            print("########## Calculate Regression Exposure %s %s %s %s %s %s ##########"
                  % (fund, period_beg_date, period_end_date, quarter_date, len(data_periods), stock_ratio))

            if len(data_periods) > self.regression_period_min:

                y = data_periods.ix[:, 0].values
                x = data_periods.ix[:, 1:].values
                x_add = sm.add_constant(x)

                low_position_exposure = max(stock_ratio - position_sub, low_position_exposure)
                print(low_position_exposure)

                P = 2 * np.dot(x_add.T, x_add)
                Q = -2 * np.dot(x_add.T, y)

                G_up = np.diag(np.ones(factor_number + 1))
                G_low = - np.diag(np.ones(factor_number + 1))
                G = np.row_stack((G_up, G_low))
                h_up = np.row_stack((np.ones((factor_number, 1)) * up_style_exposure, np.array([up_position_exposure])))
                h_low = np.row_stack((np.ones((factor_number, 1)) * up_style_exposure, np.array([-low_position_exposure])))
                h = np.row_stack((h_up, h_low))

                P = matrix(P)
                Q = matrix(Q)
                G = matrix(G)
                h = matrix(h)
                try:
                    result = sol.qp(P, Q, G, h)
                    params_add = pd.DataFrame(np.array(result['x'][1:]), columns=[period_end_date], index=barra_name).T
                    print(params_add)
                except:
                    params_add = pd.DataFrame([], columns=[period_end_date], index=barra_name).T
                    print(params_add)

            else:
                params_add = pd.DataFrame([], columns=[period_end_date], index=barra_name).T
                print(params_add)

            if i_date == 0:
                params_new = params_add
            else:
                params_new = pd.concat([params_new, params_add], axis=0)

        # 合并新数据
        ####################################################################
        out_path = Parameter().get_read_file(self.regression_exposure_name)
        out_file = os.path.join(out_path, 'Fund_Regression_Exposure_' + fund + '.csv')

        if os.path.exists(out_file):
            params_old = pd.read_csv(out_file, index_col=[0], encoding='gbk')
            params_old.index = params_old.index.map(str)
            params = pandas_add_row(params_old, params_new)
        else:
            params = params_new
        print(params)
        params.to_csv(out_file)

    def cal_fund_regression_exposure_all(self, beg_date, end_date, period="M", fund_pool="基金持仓基准基金池"):

        quarter_date = Date().get_last_fund_quarter_date(end_date)
        fund_pool = FundPool().get_fund_pool_code(quarter_date, fund_pool)

        for i_fund in range(0, len(fund_pool)):
            fund_code = fund_pool[i_fund]
            self.cal_fund_regression_exposure(fund_code, beg_date, end_date, period)

    def get_fund_regression_exposure(self, fund):

        out_path = Parameter().get_read_file(self.regression_exposure_name)
        out_file = os.path.join(out_path, 'Fund_Regression_Exposure_' + fund + '.csv')
        exposure = pd.read_csv(out_file, index_col=[0], encoding='gbk')
        exposure.index = exposure.index.map(str)
        return exposure

    def get_fund_regression_exposure_date(self, fund, date):

        exposure = self.get_fund_regression_exposure(fund)
        exposure = pd.DataFrame(exposure.ix[date, :].values, index=exposure.columns, columns=[fund])
        return exposure


class FundExposure(FundHolderExposure, FundRegressionExposure):

    """
    FundHolderExposure()
    利用年度和半年度持仓信息计算当时基金的 Barra 因子暴露

    FundRegressionExposure()
    利用有约束的线性回归的方法推测当前基金的 Barra 风格暴露
    """
    def __init__(self):

        FundHolderExposure.__init__(self)
        FundRegressionExposure.__init__(self)


if __name__ == "__main__":

    # fund = '000001.OF'
    # FundExposure().cal_fund_regression_exposure(fund, beg_date, end_date)
    # FundExposure().cal_fund_holder_exposure(fund, "20031231", end_date)
    # FundExposure().cal_fund_holder_exposure_all("20031231", "20180713", "东方红基金")
    # FundExposure().cal_fund_regression_exposure_all("20031231", "20180713", period="M", fund_pool="东方红基金")

    print(FundHolderExposure().get_fund_holder_exposure_date("000001.OF", "20171229"))
    print(FundHolderExposure().get_fund_holder_exposure("000001.OF", type_list=["STYLE", "COUNTRY"]))
