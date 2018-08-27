import pandas as pd
from datetime import datetime
import os
from quant.param.param import Parameter
from quant.stock.date import Date
from quant.stock.index_weight import IndexWeight
from quant.stock.barra import Barra
from quant.utility_fun.pandas_fun import pandas_add_row
from WindPy import w
w.start()


class IndexBarraExposure(object):

    """
    利用指数的持仓来计算指数barra_exposure

    """

    def __init__(self):

        self.barra_exposure_name = "Index_Barra_Exposure"
        self.path = Parameter().get_read_file(self.barra_exposure_name)

    def cal_index_exposure_date(self, index_code, date):

        print(" Calculating Index %s Barra Exposure at %s" % (index_code, date))
        try:
            weight = IndexWeight().get_weight(index_code=index_code, date=date)
            exposure = Barra().get_factor_exposure_date(date, type_list=["STYLE", "COUNTRY", "INDUSTRY"])

            data = pd.concat([weight, exposure], axis=1)
            data = data.dropna(subset=["WEIGHT"])

            res = pd.DataFrame([], columns=exposure.columns, index=[date])

            for i_col in range(len(exposure.columns)):
                risk_factor_name = exposure.columns[i_col]
                res.ix[date, risk_factor_name] = (data["WEIGHT"] * data[risk_factor_name]).sum()
        except:
            res = pd.DataFrame([])
        return res

    def cal_index_exposure_period(self, index_code="000300.SH",
                                  beg_date="20031231", end_date=datetime.today().strftime("%Y%m%d"),
                                  period="D"):

        date_series_daily = Date().get_trade_date_series(beg_date, end_date, period=period)

        for i_date in range(len(date_series_daily)):

            date = date_series_daily[i_date]
            res = self.cal_index_exposure_date(index_code, date)

            if i_date == 0:
                new_data = res
            else:
                new_data = pd.concat([new_data, res], axis=0)

        out_file = os.path.join(self.path,  "Index_Barra_Exposure_" + index_code + '.csv')
        if os.path.exists(out_file):
            data = pd.read_csv(out_file, encoding='gbk', index_col=[0])
            data.index = data.index.map(str)
            data = pandas_add_row(data, new_data)
        else:
            data = new_data
        data.to_csv(out_file)

    def get_index_exposure_date(self, index_code, date, type_list=["STYLE"]):

        try:
            date = Date().get_trade_date_offset(date, 0)
            out_file = os.path.join(self.path, "Index_Barra_Exposure_" + index_code + '.csv')
            data = pd.read_csv(out_file, encoding='gbk', index_col=[0])
            data.index = data.index.map(str)
            factor_name = Barra().get_factor_name(type_list=type_list)
            factor_name = list(factor_name["NAME_EN"].values)
            exposure_date = data.ix[date, factor_name]
            exposure_date = pd.DataFrame(exposure_date.values, index=exposure_date.index, columns=[index_code]).T
        except:
            print("读取出现问题")
            exposure_date = pd.DataFrame([])

        return exposure_date


if __name__ == "__main__":

    index = IndexBarraExposure()
    index.cal_index_exposure_period("000300.SH", beg_date="20180630", end_date="20180719")
    index.cal_index_exposure_period("000905.SH", beg_date="20180630", end_date="20180719")
    index.cal_index_exposure_period("881001.WI", beg_date="20180630", end_date="20180719")
    index.cal_index_exposure_period("000016.SH", beg_date="20180630", end_date="20180719")
    print(index.get_index_exposure_date("000300.SH", "20180718"))
