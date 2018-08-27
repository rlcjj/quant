import xlsxwriter
import pandas as pd
import numpy as np
from xlsxwriter.utility import *
from quant.utility_fun.if_type import is_number


class WriteExcel(object):

    def __init__(self, filename):
        self.filename = filename
        self.workbook = xlsxwriter.Workbook(filename)

    def add_worksheet(self, sheet_name):
        worksheet = self.workbook.add_worksheet(sheet_name)
        return worksheet

    def close(self):
        self.workbook.close()

    def change_pandas_index(self, df):
        df["index"] = df.index
        col = list(range(len(df.columns) - 1))
        col.insert(0, len(df.columns) - 1)
        df = df.iloc[:, col]
        return df

    def write_pandas(self, data, worksheet, begin_row_number=0, begin_col_number=1,
                     num_format_pd=None, color="orange", fillna=True):

        # 修改 dataframe 的格式

        data = self.change_pandas_index(data)

        if num_format_pd is None:
            num_format_pd = pd.DataFrame([], columns=data.columns, index=['format'])
            for i_col in range(len(data.columns)):
                col = data.columns[i_col]
                if (is_number(data.ix[0, col])) and (max(data.ix[:, col]) < 10):
                    num_format_pd.ix['format', col] = '0.00%'
                else:
                    num_format_pd.ix['format', :] = '0.00'
        else:
            num_format_pd = self.change_pandas_index(num_format_pd)
            num_format_pd.ix['format', 'index'] = ""

        if fillna:
            for i_col in range(len(data.columns)):
                col = data.columns[i_col]
                if type(data.ix[0, col]) in [np.int, np.float]:
                    data[col] = data[col].fillna(0.0)
                else:
                    data[col] = data[col].fillna("")

        col_number = data.shape[1]

        # 表头格式
        format_header = self.workbook.add_format()
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
            format_text = self.workbook.add_format()
            format_text.set_font_size(9)
            format_text.set_font_name("微软雅黑")
            format_text.set_align('center')
            format_text.set_align('vcenter')
            format_text.set_border(1)
            format_text.set_shrink()
            format_text.set_num_format(num_format_pd.iloc[0, c])

            worksheet.write_column(begin_row_number + 1, begin_col_number + c, data.iloc[:, c].values, format_text)

            # 如果是字符串的话 考虑表格宽度
            if type(data.iloc[0, c]) == np.str:
                try:
                    col_len = len(data.columns[c].encode('utf-8'))
                except:
                    col_len = 5
                text_len = max(list(data.iloc[:, c].map(lambda x: len(str(x).encode('utf-8')))))
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

        return True

    def line_chart_time_series_plot(self, worksheet, row_number, col_number, data_pd,
                                     series_name, chart_name, insert_pos):

        line_chart = self.workbook.add_chart({'type': 'line'})

        for i in range(len(data_pd.columns)):

            col = data_pd.columns[i]
            line_chart.add_series(
                {'name': series_name[0],
                 'categories': [series_name[0], row_number, col_number, row_number + len(data_pd), col_number],
                 'values': [series_name[0], row_number, col_number + 1, row_number + len(data_pd), col_number + 1],
                 'line': {'width': 1.5}
                 })

        #######################################################################################
        line_chart.set_style(11)
        line_chart.set_title({'name': chart_name,
                              'name_font': {
                                  'name': '微软雅黑', 'size': 12}
                              })

        #######################################################################################
        line_chart.set_x_axis({'num_font': {'name': '微软雅黑', 'size': 8, 'rotation': -45},
                               'minor_gridlines': {'visible': False},
                               'major_gridlines': {'visible': False},
                               'date_axis': True,
                               'num_format': 'dd/mm/yyyy',
                               'interval_tick': 10
                               })
        line_chart.set_y_axis({'num_font': {'name': '微软雅黑', 'size': 8},
                               'minor_gridlines': {'visible': False},
                               'major_gridlines': {'visible': False}
                               })
        #######################################################################################
        line_chart.set_legend({'position': 'bottom',
                               'font': {'name': '微软雅黑', 'size': 10},
                               })

        #######################################################################################
        worksheet.insert_chart(insert_pos, line_chart)
        #######################################################################################
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

    num_format_pd = pd.DataFrame([], columns=data.columns, index=['format'])
    num_format_pd.ix['format', :] = '0.00%'

    # WriteExcel
    ####################################################################################################################

    save_path = 'C:\\Users\\doufucheng\OneDrive\Desktop\\'
    begin_row_number = 0
    begin_col_number = 1
    color = "red"
    file_name = save_path + "读写EXCEL测试.xlsx"
    sheet_name = "读写EXCEL测试"

    excel = WriteExcel(file_name)
    worksheet = excel.add_worksheet(sheet_name)
    excel.write_pandas(data, worksheet, begin_row_number=0, begin_col_number=1,
                       num_format_pd=num_format_pd, color="orange", fillna=True)
    excel.close()
    ####################################################################################################################
