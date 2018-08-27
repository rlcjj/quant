import xlsxwriter
import pandas as pd
import numpy as np
from xlsxwriter.utility import *


def change_pandas_index(df):

    df[df.index.name] = df.index
    col = list(range(len(df.columns) - 1))
    col.insert(0, len(df.columns) - 1)
    df = df.iloc[:, col]
    return df


def write_pandas(file_name, sheet_name, begin_row_number, begin_col_number, data, num_format_pd, color="orange",
                 fillna=True):

    workbook = xlsxwriter.Workbook(file_name)
    worksheet = workbook.add_worksheet(sheet_name)

    # 修改 dataframe 的格式
    data = change_pandas_index(data)
    num_format_pd = change_pandas_index(num_format_pd)
    # num_format_pd.ix[0, 'mfc'] = '0.00'
    if fillna:
        data = data.fillna("")
    col_number = data.shape[1]

    # 表头格式
    format_header = workbook.add_format()
    format_header.set_font_size(9)
    format_header.set_font_name("微软雅黑")
    format_header.set_align('center')
    format_header.set_border(1)
    format_header.set_align('vcenter')
    format_header.set_shrink()
    format_header.set_bold(1)
    format_header.set_bg_color(color)

    # 写入行表头
    worksheet.write_row(begin_row_number, begin_col_number, data.columns.values, format_header)

    # 循环写入列
    for c in range(col_number):

        # 格式
        format_text = workbook.add_format()
        format_text.set_font_size(9)
        format_text.set_font_name("微软雅黑")
        format_text.set_align('center')
        format_text.set_align('vcenter')
        format_text.set_border(1)
        format_text.set_shrink()
        format_text.set_num_format(num_format_pd.iloc[0, c])

        worksheet.write_column(begin_row_number + 1, begin_col_number + c, data.iloc[:, c].values, format_text)

        # 如果是字符串的话 考虑表格宽度
        if type(data.iloc[1, c]) == np.str:
            try:
                col_len = len(data.columns[c].encode('utf-8'))
            except:
                col_len = 5
            text_len = max(list(data.iloc[:, c].map(lambda x: len(x.encode('utf-8')))))
            cell_len = 3.5 + 0.4 * max(col_len, text_len)
            column = xl_col_to_name(begin_col_number + c)
            column = column + ":" + column
            worksheet.set_column(column, cell_len)
        else:
            try:
                col_len = len(data.columns[c].encode('utf-8'))
            except:
                col_len = 5
            cell_len = 3.5 + 0.4 * col_len
            column = xl_col_to_name(begin_col_number + c)
            column = column + ":" + column
            worksheet.set_column(column, cell_len)

    workbook.close()
    return True


if __name__ == '__main__':

    # 生成数据
    ####################################################################################################################
    my_data = pd.DataFrame([], index=pd.date_range(start='20171231', end='20180430'))
    my_data.index = my_data.index.map(lambda x: x.strftime('%Y-%m-%d'))
    my_data['数字'] = np.random.random((my_data.shape[0], 1)) * 100
    my_data['Ratio'] = np.random.random((my_data.shape[0], 1))
    my_data['整数'] = list(map(int, np.random.random((my_data.shape[0], 1)) * 100))
    my_data['字符串'] = '中文测试'
    data = my_data

    num_format_pd = pd.DataFrame([], columns=my_data.columns, index=['format'])
    num_format_pd.ix['format', :] = '0.00'
    num_format_pd.ix['format', 'Ratio'] = '0.00%'

    save_path = 'C:\\Users\\doufucheng\OneDrive\Desktop\\'
    begin_row_number = 0
    begin_col_number = 1
    color = "red"
    file_name = save_path + "读写EXCEL测试.xlsx"
    sheet_name = "读写EXCEL测试"

    write_pandas(file_name, sheet_name, begin_row_number, begin_col_number, data, num_format_pd, color)



