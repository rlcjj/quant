from quant.stock.stock import Stock
import os
import pandas as pd
from quant.utility_fun.write_excel import WriteExcel


def Alpha_Date():

    print("#################### 开始检查更新日期 Alpha 数据 ####################")
    path = "E:\\3_Data\\5_stock_data\\3_alpha_model\\"
    file = "MyAlpha.xlsx"

    data = pd.read_excel(os.path.join(path, file), encoding='gbk')
    result = pd.DataFrame([], columns=['开始日期', '结束日期'], index=data["因子名"].values)

    for i in range(0, len(data)):

        factor_name = data.ix[i, "因子名"]

        try:
            print("#################### 最后更新日期 %s 数据 ####################" % factor_name)
            factor = Stock().get_factor_h5(factor_name, None, 'alpha_dfc')
            result.ix[factor_name, '开始日期'] = factor.columns[0]
            result.ix[factor_name, '结束日期'] = factor.columns[-1]
            result.ix[factor_name, "最后一天有效数据个数"] = factor.ix[:, -1].count()
            result.ix[factor_name, "最后一天股票个数"] = len(factor.ix[:, -1])
            result.ix[factor_name, "最后一天有效数据比率"] = factor.ix[:, -1].count() / len(factor.ix[:, -1])
        except:
            print("#################### %s 数据 为空 ！！！####################" % factor_name)

    print("#################### 存储 日期检查结果数据 ####################")
    filename = os.path.join(path, "Alpha_Date.xlsx")
    sheet_name = "Alpha_Date"

    we = WriteExcel(filename)
    ws = we.add_worksheet(sheet_name)

    num_format_pd = pd.DataFrame([], columns=result.columns, index=['format'])
    num_format_pd.ix['format', :] = '0'
    num_format_pd.ix['format', ['最后一天有效数据比率']] = '0.00%'
    we.write_pandas(result, ws, begin_row_number=0, begin_col_number=1,
                    num_format_pd=num_format_pd, color="blue", fillna=True)

    we.close()

    print("#################### 结束检查更新日期 Alpha 数据 ####################")

if __name__ == '__main__':

    Alpha_Date()
