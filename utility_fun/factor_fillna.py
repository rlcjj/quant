

class FactorFillNa(object):


    """
    补充因子的缺失值
    补充范围： 自上市之日起 到退市之日终止
    1、补充当日截面的中位数
    2、补充对应行业的中位数
    3、因子值根据其他因子值做线性回归得到 (Barra Risk Model)
    """

    def __init__(self):
        pass

    def fillna_all_mad(self, data):


        pass

        # factor_pandas = data.copy()
        # factor_pandas = factor_pandas.dropna(how='all')
        # factor_val = factor_pandas.values
        #
        # name = '是否上市'
        # if_list = get_cal_data(name)
        # if_list = if_list.ix[factor_pandas.index.values, factor_pandas.columns.values]
        # if_list = if_list[~if_list.index.duplicated()]
        # if_nan = factor_pandas.isnull()
        #
        # mask_val = (if_list & if_nan).values
        # md_val = factor_pandas.median(axis=1).values
        # md_remat_val = np.tile(np.vstack(md_val), (1, factor_pandas.shape[1]))
        # factor_fill_mad_val = np.where(mask_val, md_remat_val, factor_val)
        # factor_fill_mad_pandas = pd.DataFrame(factor_fill_mad_val, index=factor_pandas.index,
        #                                       columns=factor_pandas.columns)
        #
        # return factor_fill_mad_pandas

if __name__ == '__main__':

    pass