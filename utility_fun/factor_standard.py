import pandas as pd
from quant.utility_fun.factor_operate import FactorOperate
from scipy.stats import norm
from quant.stock.stock_factor_read_write import StockFactorReadWrite


class FactorStandard(object):

    """
    对 Series 或者 DataFrame 类型的数据 进行操作

    逆正态化（正态化）：根据排名 转化为百分比 再转化为正态值
    标准化：减去均值 除以标准差 只是标准化 并没有正态化
    按照自由流通市值标准化

    inv_normalization()
    standardization()
    standardization_free_mv()

    """
    def __init__(self):
        pass

    def inv_normalization(self, data):

        """
        这里的（逆）正态化是 先给计算排名 给出分位数 再给出标准正太分布中的具体值
        """

        if type(data) == pd.Series:

            data_series = data.copy()
            data_series = data_series.rank() / data_series.count()
            data_series = pd.Series(norm.ppf(list(data_series.values), 0, 1),
                                    index=data.index, name=data.name)

            return data_series

        elif type(data) == pd.DataFrame:

            factor = data.copy()
            factor_percentile = factor.rank() / factor.count()
            factor_value = pd.DataFrame(norm.ppf(list(factor_percentile.values), 0, 1),
                                        index=data.index, columns=data.columns)
            return factor_value
        else:
            print(" Type of Data can not be remove extreme value ")
            return None

    def standardization(self, data):
        if type(data) == pd.Series:

            data_series = data.copy()
            mean = data_series.mean()
            std = data_series.std()
            normal_series = (data_series - mean) / std
            return normal_series

        elif type(data) == pd.DataFrame:

            factor = data.copy()
            factor = factor.T

            mean = factor.mean(axis=1)
            std = factor.std(axis=1)
            factor = factor.sub(mean, axis='index')
            factor = factor.div(std, axis="index")
            factor = factor.T
            return factor

        else:
            print(" Type of Data can not be remove extreme value ")
            return None

    def standardization_free_mv(self, data, date=None):
        """
        均值为市值加权均值 标准差为普通标准差 Barra 做法
        """

        if type(data) == pd.Series:

            if date is None:
                date = data.name

            data_series = data.copy()

            free_marketvalue = StockFactorReadWrite().get_factor_h5("Mkt_freeshares", None, 'primary_mfc')
            free_marketvalue_series = free_marketvalue[date]

            [data_series, free_marketvalue_series] = \
                FactorOperate().make_same_index_columns([data_series, free_marketvalue_series])
            free_marketvalue_series = free_marketvalue_series / free_marketvalue_series.sum()
            free_marketvalue_series = free_marketvalue_series.fillna(0.0)

            # data_series = data_series.fillna(0.0)
            mean_weight_free_mv = data_series.mul(free_marketvalue_series).sum()

            std = data_series.std()
            normal_series = (data_series - mean_weight_free_mv) / std
            return normal_series

        elif type(data) == pd.DataFrame:

            factor = data.copy()
            free_marketvalue = StockFactorReadWrite().get_factor_h5("Mkt_freeshares", None, 'primary_mfc')
            [factor, free_marketvalue] = FactorOperate().make_same_index_columns([factor, free_marketvalue])
            free_marketvalue = free_marketvalue / free_marketvalue.sum()
            free_marketvalue = free_marketvalue.fillna(0.0)
            free_marketvalue = free_marketvalue.T

            # factor = factor.fillna(0.0)
            factor = factor.T

            mean_weight_free_mv = factor.mul(free_marketvalue).sum(axis=1)

            std = factor.std(axis=1)
            factor = factor.sub(mean_weight_free_mv, axis='index')
            factor = factor.div(std, axis="index")
            factor = factor.T
            return factor

        else:
            print(" Type of Data can not be remove extreme value ")
            return None


if __name__ == '__main__':

    # Data
    ###################################################################

    name = 'EP_Roll'
    data_pandas = StockFactorReadWrite().get_factor_h5(name, None, "alpha_mfc")
    data_series = data_pandas["20171229"]

    # Series
    ###################################################################

    inv_normalization_series = FactorStandard().inv_normalization(data_series)
    standardization_series = FactorStandard().standardization(data_series)
    standardization_series_mv = FactorStandard().standardization_free_mv(data_series)

    result = pd.concat([data_series, inv_normalization_series,
                        standardization_series, standardization_series_mv], axis=1)
    result.columns = ["raw_data", 'normal', 'standard', "standard_mv"]
    print(result[result['raw_data'] > 0.15])
    # print(result)

    # DataFrame
    ###################################################################

    inv_normalization_pandas = FactorStandard().inv_normalization(data_pandas)
    standardization_pandas = FactorStandard().standardization(data_pandas)
    standardization_pandas_mv = FactorStandard().standardization_free_mv(data_pandas)

    result = pd.concat([data_pandas["20171229"], inv_normalization_pandas["20171229"],
                        standardization_pandas["20171229"], standardization_pandas_mv["20171229"]], axis=1)

    result.columns = ["raw_data", 'normal', 'standard', "standard_mv"]
    print(result[result['raw_data'] > 0.15])
    # print(result)
    ###################################################################

