import pandas as pd
import numpy as np
from datetime import datetime
import os
from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.utility_fun.factor_preprocess import FactorPreProcess
from quant.utility_fun.write_excel import WriteExcel
import matplotlib.pyplot as plt


def cal_factor_alpha_return(factor_name, beg_date, end_date, cal_period):

    # param
    ###############################################################################################################
    ###############################################################################################################
    group_number = 5
    year_trade_days = 242
    out_path = 'E:\\3_Data\\5_stock_data\\2_risk_model\\1_barra_risk_model\\'

    alpha_remove_extreme_value = True  # alpha 因子 取极值
    alpha_standard = True  # alpha 因子 标准化

    # read data
    ###############################################################################################################
    ###############################################################################################################
    price = Stock().get_factor_h5("PriceCloseAdjust", None, "primary_dfc")
    risk_val = Stock().get_factor_h5(factor_name, None, "barra_risk_dfc")

    beg_date = max(beg_date, price.columns[0], risk_val.columns[0])
    end_date = min(end_date, price.columns[-1], risk_val.columns[-1])
    date_series = Date().get_trade_date_series(beg_date, end_date, period=cal_period)

    # pre process data
    ###############################################################################################################
    ###############################################################################################################
    if alpha_remove_extreme_value:
        risk_val = FactorPreProcess().remove_extreme_value_mad(risk_val)

    if alpha_standard:
        risk_val = FactorPreProcess().standardization(risk_val)

    # cal everyday
    ###############################################################################################################
    ###############################################################################################################
    risk_return = pd.DataFrame([], index=date_series)
    risk_exposure = pd.DataFrame([], index=date_series, columns=price.index)

    for i_date in range(len(date_series) - 2):

        cur_cal_date = date_series[i_date]
        next_cal_date = date_series[i_date + 1]
        buy_date = Date().get_trade_date_offset(cur_cal_date, 1)
        sell_date = Date().get_trade_date_offset(next_cal_date, 1)
        print(" Calculating Factor %s Risk Return At %s" % (factor_name, cur_cal_date))

        risk_return.index.name = 'CalDate'
        risk_return.ix[cur_cal_date, "BuyDate"] = buy_date
        risk_return.ix[cur_cal_date, "SellDate"] = sell_date

        risk_date = risk_val[cur_cal_date]
        buy_price = price[buy_date]
        sell_price = price[sell_date]
        pct_date = sell_price / buy_price - 1.0

        risk_date = FactorPreProcess().remove_extreme_value_mad(risk_date)
        risk_date = FactorPreProcess().standardization(risk_date)
        risk_exposure.ix[cur_cal_date, :] = risk_date

        res = pd.concat([risk_date, pct_date], axis=1)
        res.columns = ['risk_val', 'period_pct']
        res = res.dropna()
        res = res.sort_values(by=['risk_val'], ascending=False)

        labels = ["group_" + str(i) for i in list(range(1, group_number + 1))]
        res['group'] = pd.cut(res['risk_val'], bins=group_number, labels=labels)

        period_return = (res['risk_val'] * res['period_pct']).mean()
        risk_return.ix[cur_cal_date, "FactorReturn"] = period_return

        information_correlation = res['risk_val'].corr(res['period_pct'])
        risk_return.ix[cur_cal_date, "IC"] = information_correlation

        group_pct = res.groupby(by=['group'])['period_pct'].mean()
        for i_label in range(len(labels)):
            risk_return.ix[cur_cal_date, labels[i_label]] = group_pct.values[i_label]

    risk_return = risk_return.dropna(subset=['FactorReturn'])
    risk_return["CumFactorReturn"] = risk_return['FactorReturn'].cumsum()
    cum_labels = ["Cum_" + str(x) for x in labels]
    risk_return[cum_labels] = risk_return[labels].cumsum()

    # plot
    ###############################################################################################################
    ###############################################################################################################
    plt_col = []
    plt_col.append("CumFactorReturn")
    plt_col.extend(cum_labels)
    risk_return[plt_col].plot()
    plt.show()

    # describe annual
    ###############################################################################################################
    ###############################################################################################################

    back_test_beg_date = Date().get_trade_date_offset(date_series[0], 1)
    back_test_end_date = Date().get_trade_date_offset(date_series[len(date_series) - 1], 1)
    back_test_days = Date().get_trade_date_diff(back_test_beg_date, back_test_end_date)

    backtest_year = back_test_days / year_trade_days

    risk_return['IC_abs'] = risk_return['IC'].abs()
    risk_return['year'] = risk_return.index.map(lambda x: datetime.strptime(x, "%Y%m%d").year)

    year_factor_return = risk_return.groupby(by=['year'])['FactorReturn'].sum()
    year_count = risk_return.groupby(by=['year'])['FactorReturn'].count()
    year_ic_mean = risk_return.groupby(by=['year'])['IC'].mean()
    year_ic_abs_mean = risk_return.groupby(by=['year'])['IC_abs'].mean()
    year_ic_std = risk_return.groupby(by=['year'])['IC'].std()
    year_gp_mean = risk_return.groupby(by=['year'])[labels].mean()

    year_describe = pd.concat([year_factor_return, year_count, year_ic_mean, year_ic_abs_mean,
                               year_ic_std, year_gp_mean], axis=1)
    col = ['YearFactorReturn', 'Count', 'IC_mean', 'IC_abs_mean', 'IC_std']
    col.extend(labels)
    year_describe.columns = col

    year_describe['YearFactorReturn'] = year_describe['YearFactorReturn'] / year_describe['Count'] * year_count
    year_describe['IC_IR'] = year_describe['IC_mean'] / year_describe['IC_std'] * np.sqrt(50)

    year_describe.ix['Sum', 'YearFactorReturn'] = risk_return["CumFactorReturn"].values[-1] / backtest_year
    year_describe.ix['Sum', 'IC_IR'] = risk_return["IC"].mean() / risk_return["IC"].std() * np.sqrt(50)
    year_describe.ix['Sum', 'IC_mean'] = risk_return["IC"].mean()
    year_describe.ix['Sum', 'IC_abs_mean'] = risk_return["IC"].abs().mean()
    year_describe.ix['Sum', 'IC_std'] = risk_return["IC"].std()
    year_describe.ix['Sum', labels] = year_describe.ix[0:-1, labels].sum()
    year_describe.index = year_describe.index.map(str)

    for i in range(len(year_describe)):
        year = year_describe.index[i]
        corr_pd = pd.DataFrame(year_describe.ix[year, labels].values, index=labels, columns=['group_return'])
        corr_pd['group_number'] = (list(range(1, group_number + 1)))
        year_describe.ix[year, 'Group_Corr'] = corr_pd.corr().ix[0, 1]

    # save data
    ###############################################################################################################
    ###############################################################################################################

    # exposure_corr
    ###############################################################################################################
    risk_exposure = risk_exposure.astype(np.float)
    exposure_corr = pd.DataFrame([], index=risk_exposure.index, columns=['Exposure_Corr'])

    for i_date in range(1, len(risk_exposure.index)):
        last_exposure_date = risk_exposure.index[i_date - 1]
        cur_exposure_date = risk_exposure.index[i_date]
        exposure_adjoin = risk_exposure.ix[last_exposure_date:cur_exposure_date, :]
        exposure_adjoin = exposure_adjoin.T.dropna()
        exposure_corr.ix[cur_exposure_date, 'Exposure_Corr'] = exposure_adjoin.corr().ix[0, 1]

    exposure_corr = exposure_corr.dropna()
    exposure_corr.ix['Mean', 'Exposure_Corr'] = exposure_corr['Exposure_Corr'].mean()
    filename = os.path.join(out_path, 'risk_exposure_stability', factor_name + "_FactorExposureCorr.csv")
    exposure_corr.to_csv(filename)

    # Factor Return
    ###############################################################################################################
    filename = os.path.join(out_path, 'risk_return', factor_name + "_FactorReturn.xlsx")
    sheet_name = "FactorReturn"

    we = WriteExcel(filename)
    ws = we.add_worksheet(sheet_name)

    num_format_pd = pd.DataFrame([], columns=year_describe.columns, index=['format'])
    num_format_pd.ix['format', :] = '0.00%'
    num_format_pd.ix['format', ['Count', 'IC_IR']] = '0.00'
    we.write_pandas(year_describe, ws, begin_row_number=0, begin_col_number=1,
                    num_format_pd=num_format_pd, color="blue", fillna=True)

    num_format_pd = pd.DataFrame([], columns=risk_return.columns, index=['format'])
    num_format_pd.ix['format', :] = '0.00%'
    num_format_pd.ix['format', ['year']] = '0'
    we.write_pandas(risk_return, ws, begin_row_number=0, begin_col_number=2 + len(year_describe.columns),
                    num_format_pd=num_format_pd, color="blue", fillna=True)
    we.close()
    ###############################################################################################################


if __name__ == '__main__':

    cal_period = "W"
    beg_date = "20040101"
    end_date = datetime.today().strftime("%Y%m%d")

    factor_name_list = ["NORMAL_CNE5_SIZE", "NORMAL_CNE5_BETA", "NORMAL_CNE5_MOMENTUM", "NORMAL_CNE5_NON_LINEAR_SIZE"]
    factor_name_list = ['NORMAL_CNE5_CUBE_SIZE']

    for i in range(len(factor_name_list)):
        factor_name = factor_name_list[i]
        cal_factor_alpha_return(factor_name, beg_date, end_date, cal_period)
