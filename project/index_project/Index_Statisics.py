from quant.stock.index import Index
from datetime import datetime
import pandas as pd

"""
一半中证500 一半中证全债 统计持有三年后收益的分布
"""

def MyCumSum(l):

    l = list(l)
    nav = [x + 1.0 for x in l]

    r = 1.0
    for i in range(len(nav)):
        r *= nav[i]

    return r - 1.0


def IndexStatisics():

    index_code_1 = 'H11001.CSI'
    index_code_2 = '000905.SH'
    weight_1 = 0.5
    weight_2 = 1 - weight_1
    holding_days = 3 * 250
    beg_date = '20040101'
    end_date = datetime.today().strftime('%Y%m%d')
    path = 'C:\\Users\\doufucheng\OneDrive\Desktop\\'

    index_code_pct_1 = Index().get_index_factor(index_code_1, beg_date, end_date, ['PCT'])
    index_code_pct_2 = Index().get_index_factor(index_code_2, beg_date, end_date, ['PCT'])

    index_code_pct = index_code_pct_1 * weight_1 + index_code_pct_2 * weight_2
    index_code_pct = index_code_pct.dropna()

    sum_index = index_code_pct.rolling(window=holding_days).apply(MyCumSum)
    sum_index = sum_index.dropna()
    sum_index.to_csv(path + 'Return.csv')
    sum_index['Type'] = pd.cut(sum_index['PCT'], bins=[-0.30, -0.10, 0.0, 0.20, 0.40, 0.60, 0.80, 1.00, 2.00])
    sum_index_g = sum_index.groupby(by=['Type']).count()

    print(" Begin Date ", sum_index.index[0])
    sum_index_g.to_csv(path + 'Statisics.csv')



if __name__ == '__main__':

    print(MyCumSum([0.02, 0.03, -0.05]))
    IndexStatisics()
