import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from datetime import datetime
import statsmodels.api as sm
from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.utility_fun.factor_preprocess import FactorPreProcess
from quant.utility_fun.write_excel import WriteExcel


def factor_neutral(factor_series, neutral_frame):

    """
    中性化
    """

    concat_data = pd.concat([factor_series, neutral_frame], axis=1)
    concat_data = concat_data.dropna()

    factor_val = concat_data.ix[:, 0]
    neutral_val = concat_data.ix[:, 1:]

    model = sm.OLS(factor_val.values, neutral_val.values)
    regress = model.fit()

    params = regress.params
    params = pd.DataFrame(params, index=neutral_val.columns, columns=['param'])
    factor_res = factor_val - regress.predict(neutral_val)

    return params, factor_res


def cal_factor_alpha_return(factor_name, beg_date, end_date, cal_period):

    # param
    ###############################################################################################################
    ###############################################################################################################
    group_number = 8
    year_trade_days = 242
    min_stock_number = 100
    out_path = 'E:\\3_Data\\5_stock_data\\3_alpha_model\\'

    alpha_remove_extreme_value = True  # alpha 因子 取极值
    alpha_standard = True  # alpha 因子 标准化
    alpha_industry_neutral = True  # alpha 因子 行业中性
    alpha_barra_style_neutral = True  # alpha 因子 风格中性

    # read data
    ###############################################################################################################
    ###############################################################################################################
    price = Stock().get_factor_h5("PriceCloseAdjust", None, "alpha_dfc")
    alpha_val = Stock().get_factor_h5(factor_name, None, "alpha_dfc")
    industry = Stock().get_factor_h5("industry_citic1", None, "primary_mfc")
    industry = industry.applymap(lambda x: x.decode('utf-8'))
    
    [alpha_val, industry] = FactorPreProcess().make_same_index_columns([alpha_val, industry])
    
    if alpha_barra_style_neutral:
        
        size = Stock().get_factor_h5("NORMAL_CNE5_SIZE", None, 'barra_risk_dfc')
        beta = Stock().get_factor_h5("NORMAL_CNE5_BETA", None, 'barra_risk_dfc')
        nolin_size = Stock().get_factor_h5("NORMAL_CNE5_NON_LINEAR_SIZE", None, 'barra_risk_dfc')
        momentum = Stock().get_factor_h5("NORMAL_CNE5_MOMENTUM", None, 'barra_risk_dfc')

        [size, beta, nolin_size] = FactorPreProcess().make_same_index_columns([size, beta, nolin_size])
        beg_date = max(beg_date, price.columns[0], alpha_val.columns[0], beta.columns[0])
        end_date = min(end_date, price.columns[-1], alpha_val.columns[-1], beta.columns[-1])

    else:
        beg_date = max(beg_date, price.columns[0], alpha_val.columns[0])
        end_date = min(end_date, price.columns[-1], alpha_val.columns[-1])

    date_series = Date().get_trade_date_series(beg_date, end_date, period=cal_period)
    date_series = list(set(date_series) & set(alpha_val.columns))
    date_series.sort()

    # pre process data
    ###############################################################################################################
    ###############################################################################################################
    if alpha_remove_extreme_value:
        alpha_val = FactorPreProcess().remove_extreme_value_mad(alpha_val)

    if alpha_standard:
        alpha_val = FactorPreProcess().standardization(alpha_val)

    # cal everyday
    ###############################################################################################################
    ###############################################################################################################
    alpha_return = pd.DataFrame([], index=date_series)
    alpha_exposure = pd.DataFrame([], index=date_series, columns=price.index)

    for i_date in range(len(date_series) - 2):

        cur_cal_date = date_series[i_date]
        next_cal_date = date_series[i_date + 1]
        buy_date = Date().get_trade_date_offset(cur_cal_date, 1)
        sell_date = Date().get_trade_date_offset(next_cal_date, 1)
        print(" Calculating Factor %s Alpha Return At %s" % (factor_name, cur_cal_date))

        alpha_return.index.name = 'CalDate'
        alpha_return.ix[cur_cal_date, "BuyDate"] = buy_date
        alpha_return.ix[cur_cal_date, "SellDate"] = sell_date

        alpha_date = alpha_val[cur_cal_date]
        buy_price = price[buy_date]
        sell_price = price[sell_date]
        pct_date = sell_price / buy_price - 1.0

        if alpha_industry_neutral:

            try:
                industry_date = industry[cur_cal_date]
                industry_dummy = pd.get_dummies(industry_date)
            except:
                continue

            if len(pd.concat([alpha_date, industry_date], axis=1).dropna()) < min_stock_number:
                continue
            else:
                params, factor_res = factor_neutral(factor_series=alpha_date, neutral_frame=industry_dummy)
                alpha_date = factor_res
                alpha_date = FactorPreProcess().remove_extreme_value_mad(alpha_date)
                alpha_date = FactorPreProcess().standardization(alpha_date)

        if alpha_barra_style_neutral:

            try:
                size_date = size[cur_cal_date]
                beta_date = beta[cur_cal_date]
                nolin_size_date = nolin_size[cur_cal_date]
                momentum_date = momentum[cur_cal_date]
            except:
                continue

            if len(pd.concat([alpha_date, size_date], axis=1).dropna()) < min_stock_number:
                continue
            else:
                barra_risk_exposure = pd.concat([beta_date, size_date,
                                                 nolin_size_date, momentum_date], axis=1)
                barra_risk_exposure.columns = ['beta', 'size', 'nolin_size', 'momentum']
                params, factor_res = factor_neutral(factor_series=alpha_date, neutral_frame=barra_risk_exposure)
                alpha_date = factor_res
                alpha_date = FactorPreProcess().remove_extreme_value_mad(alpha_date)
                alpha_date = FactorPreProcess().standardization(alpha_date)

        alpha_exposure.ix[cur_cal_date, :] = alpha_date
        res = pd.concat([alpha_date, pct_date], axis=1)
        res.columns = ['alpha_val', 'period_pct']
        res = res.dropna()
        res = res.sort_values(by=['alpha_val'], ascending=False)

        labels = ["group_" + str(i) for i in list(range(1, group_number + 1))]
        res['group'] = pd.cut(res['alpha_val'], bins=group_number, labels=labels)

        period_return = (res['alpha_val'] * res['period_pct']).mean()
        alpha_return.ix[cur_cal_date, "FactorReturn"] = period_return

        information_correlation = res['alpha_val'].corr(res['period_pct'])
        alpha_return.ix[cur_cal_date, "IC"] = information_correlation

        group_pct = res.groupby(by=['group'])['period_pct'].mean()
        for i_label in range(len(labels)):
            alpha_return.ix[cur_cal_date, labels[i_label]] = group_pct.values[i_label]

    alpha_return = alpha_return.dropna(subset=['FactorReturn'])
    alpha_return["CumFactorReturn"] = alpha_return['FactorReturn'].cumsum()
    cum_labels = ["Cum_" + str(x) for x in labels]
    alpha_return[cum_labels] = alpha_return[labels].cumsum()

    # plot
    ###############################################################################################################
    ###############################################################################################################
    # plt_col = []
    # plt_col.append("CumFactorReturn")
    # plt_col.extend(cum_labels)
    # alpha_return[plt_col].plot()
    # plt.title(factor_name)
    # plt.show()

    # describe annual
    ###############################################################################################################
    ###############################################################################################################

    back_test_beg_date = Date().get_trade_date_offset(date_series[0], 1)
    back_test_end_date = Date().get_trade_date_offset(date_series[len(date_series) - 1], 1)
    back_test_days = Date().get_trade_date_diff(back_test_beg_date, back_test_end_date)

    backtest_year = back_test_days / year_trade_days

    alpha_return['year'] = alpha_return.index.map(lambda x: datetime.strptime(x, "%Y%m%d").year)

    year_factor_return = alpha_return.groupby(by=['year'])['FactorReturn'].sum()
    year_count = alpha_return.groupby(by=['year'])['FactorReturn'].count()
    year_ic_mean = alpha_return.groupby(by=['year'])['IC'].mean()
    year_ic_std = alpha_return.groupby(by=['year'])['IC'].std()
    year_gp_mean = alpha_return.groupby(by=['year'])[labels].mean()

    year_describe = pd.concat([year_factor_return, year_count, year_ic_mean, year_ic_std, year_gp_mean], axis=1)
    col = ['YearFactorReturn', 'Count', 'IC_mean', 'IC_std']
    col.extend(labels)
    year_describe.columns = col

    year_describe['YearFactorReturn'] = year_describe['YearFactorReturn'] / year_describe['Count'] * year_count
    year_describe['IC_IR'] = year_describe['IC_mean'] / year_describe['IC_std'] * np.sqrt(50)

    year_describe.ix['Sum', 'YearFactorReturn'] = alpha_return["CumFactorReturn"].values[-1] / backtest_year
    year_describe.ix['Sum', 'IC_IR'] = alpha_return["IC"].mean() / alpha_return["IC"].std() * np.sqrt(50)
    year_describe.ix['Sum', 'IC_mean'] = alpha_return["IC"].mean()
    year_describe.ix['Sum', 'IC_std'] = alpha_return["IC"].std()
    year_describe.ix['Sum', labels] = year_describe.ix[0:-1, labels].sum()
    year_describe.index = year_describe.index.map(str)

    for i in range(len(year_describe)):
        year = year_describe.index[i]
        corr_pd = pd.DataFrame(year_describe.ix[year, labels].values, index=labels, columns=['group_return'])
        corr_pd['group_number'] = (list(range(1, group_number+1)))
        year_describe.ix[year, 'Group_Corr'] = corr_pd.corr().ix[0, 1]

    # save data
    ###############################################################################################################
    ###############################################################################################################

    # alpha_exposure_neutral
    ###############################################################################################################
    alpha_exposure = alpha_exposure.astype(np.float)
    filename = os.path.join(out_path, 'alpha_exposure_neutral', factor_name + "_FactorExposureNeutral.csv")
    alpha_exposure.T.to_csv(filename)

    # exposure_corr
    ###############################################################################################################
    exposure_corr = pd.DataFrame([], index=alpha_exposure.index, columns=['Exposure_Corr'])

    for i_date in range(1, len(alpha_exposure.index)):
        last_exposure_date = alpha_exposure.index[i_date-1]
        cur_exposure_date = alpha_exposure.index[i_date]
        exposure_adjoin = alpha_exposure.ix[last_exposure_date:cur_exposure_date, :]
        exposure_adjoin = exposure_adjoin.T.dropna()
        exposure_corr.ix[cur_exposure_date, 'Exposure_Corr'] = exposure_adjoin.corr().ix[0, 1]

    exposure_corr = exposure_corr.dropna()
    exposure_corr.ix['Mean', 'Exposure_Corr'] = exposure_corr['Exposure_Corr'].mean()
    filename = os.path.join(out_path, 'alpha_exposure_stability', factor_name + "_FactorExposureCorr.csv")
    exposure_corr.to_csv(filename)

    # Factor Return
    ###############################################################################################################
    filename = os.path.join(out_path, 'alpha_return', factor_name + "_FactorReturn.xlsx")
    sheet_name = "FactorReturn"

    we = WriteExcel(filename)
    ws = we.add_worksheet(sheet_name)

    num_format_pd = pd.DataFrame([], columns=year_describe.columns, index=['format'])
    num_format_pd.ix['format', :] = '0.00%'
    num_format_pd.ix['format', ['Count', 'IC_IR']] = '0.00'
    we.write_pandas(year_describe, ws, begin_row_number=0, begin_col_number=1,
                    num_format_pd=num_format_pd, color="blue", fillna=True)

    num_format_pd = pd.DataFrame([], columns=alpha_return.columns, index=['format'])
    num_format_pd.ix['format', :] = '0.00%'
    num_format_pd.ix['format', ['year']] = '0'
    we.write_pandas(alpha_return, ws, begin_row_number=0, begin_col_number=2+len(year_describe.columns),
                    num_format_pd=num_format_pd, color="blue", fillna=True)
    we.close()
    ###############################################################################################################


if __name__ == '__main__':

    cal_period = "W"
    beg_date = "20040101"
    end_date = datetime.today().strftime("%Y%m%d")

    path = "E:\\3_Data\\5_stock_data\\3_alpha_model\\"
    file = "MyAlpha.xlsx"

    data = pd.read_excel(os.path.join(path, file), encoding='gbk')
    data = data[data['计算因子收益率'] == "是"]
    data = data.reset_index(drop=True)

    for i in range(0, len(data)):

        factor_name = data.ix[i, "因子名"]
        print("#################### 开始计算因子收益率 %s 数据 ####################" % factor_name)
        cal_factor_alpha_return(factor_name, beg_date, end_date, cal_period)
        print("#################### 结束计算因子收益率 %s 数据 ####################" % factor_name)

