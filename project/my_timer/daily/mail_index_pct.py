import pandas as pd
from WindPy import w
from quant.utility_fun.send_email import send_mail_qq
w.start()


# 发送今日指数临近收盘价数据，用来基金定投
def mail_index_pct():

    data = w.wsq("000300.SH,000905.SH,CI005165.WI,CI005166.WI", "rt_pct_chg,rt_date,rt_pe_ttm,rt_pb_lf")
    data = pd.DataFrame(data.Data, index=data.Fields, columns=data.Codes).T
    data['NAME'] = ["沪深300", "中证500", "中信证券二级行业指数", "中信保险二级行业指数"]

    string_total = ""
    for i in range(len(data)):
        string = str(data.ix[i, "RT_DATE"].astype(int)) + "日, " + data.ix[i, "NAME"]
        string += "现在涨幅为" + str(data.ix[i, "RT_PCT_CHG"] * 100) + '%, '
        string += "PB_LF为" + str(data.ix[i, "RT_PB_LF"].round(2)) + ', '
        string += "PE_TTM为" + str(data.ix[i, "RT_PE_TTM"].round(1)) + '.' + '\n'
        print(string)
        string_total += string

    send_mail_qq('1119332482@qq.com', 'bxfiljzifsaggdea', '今日指数涨跌幅', string_total, '1119332482@qq.com')
    send_mail_qq('1119332482@qq.com', 'bxfiljzifsaggdea', '今日指数涨跌幅', string_total, 'li_tingting92@163.com')


if __name__ == "__main__":

    mail_index_pct()
