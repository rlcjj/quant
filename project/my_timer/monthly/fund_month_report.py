import numpy as np
from win32com.client import Dispatch
import win32com
import pandas as pd
from datetime import datetime, timedelta
import calendar
from WindPy import w
w.start()


def get_date():

    today = datetime.today().strftime('%Y-%m-%d')
    last_month = (datetime.today() - timedelta(days=27)).month
    year = (datetime.today() - timedelta(days=27)).year
    date = w.tdays("2018-01-05", today, "")
    date_pd = pd.DataFrame(date.Data, columns=date.Times, index=['date']).T
    date_pd.index = date_pd.index.map(lambda x: x.strftime('%Y-%m-%d'))
    date_pd['month'] = date_pd['date'].map(lambda x: x.month)
    date_pd['year'] = date_pd['date'].map(lambda x: x.year)
    date_pd_month = date_pd[date_pd['year'] == year]
    date_pd_month = date_pd_month[date_pd_month['month'] == last_month]
    begin_date = date_pd_month.index[0]
    end_date = date_pd_month.index[len(date_pd_month) - 1]

    return begin_date, end_date


def load_index_pe(code, end_date):

    data = w.wss(code, "pe_ttm", "tradeDate=" + end_date)

    return np.round(data.Data[0][0],2)


def format_number_to_pctstr(x):
    x_str = '%.2f%%' % (x * 100.0)
    return x_str


def load_index_pct(code, begin_date, end_date):

    pct_data = w.wsd(code, "pct_chg", begin_date, end_date, "")
    pct_data_pd = pd.DataFrame(pct_data.Data, index=pct_data.Fields, columns=pct_data.Times).T
    std = (pct_data_pd['PCT_CHG'] / 100).std() * np.sqrt(250)
    pct = ((pct_data_pd['PCT_CHG']/100.0 + 1.0).cumprod() - 1.0)[len(pct_data_pd) - 1]

    return pct, std


def load_fund_pct(code, begin_date, end_date):

    pct_data = w.wsd(code, "NAV_adj_return1", begin_date, end_date, "")
    pct_data_pd = pd.DataFrame(pct_data.Data, index=['PCT_CHG'], columns=pct_data.Times).T
    std = (pct_data_pd['PCT_CHG'] / 100).std() * np.sqrt(250)
    pct = ((pct_data_pd['PCT_CHG']/100.0 + 1.0).cumprod() - 1.0)[len(pct_data_pd) - 1]

    return pct, std


def get_last_month_last_date():

    last_month = (datetime.today() - timedelta(days=27)).month
    year = (datetime.today() - timedelta(days=27)).year
    firstDayWeekDay, monthRange = calendar.monthrange(year, last_month)

    # 获取当月的第一天
    lastDay = datetime(year=year, month=last_month, day=monthRange).day
    return last_month, lastDay


def load_three_industry(begin_date, end_date):

    data = w.wsd("CI005001.WI,CI005002.WI,CI005003.WI,CI005004.WI,CI005005.WI,CI005006.WI,CI005007.WI,CI005008.WI,"
                 "CI005009.WI,CI005010.WI,CI005011.WI,CI005012.WI,CI005013.WI,CI005014.WI,CI005015.WI,CI005016.WI,"
                 "CI005017.WI,CI005018.WI,CI005019.WI,CI005020.WI,CI005021.WI,CI005022.WI,CI005023.WI,CI005024.WI,"
                 "CI005025.WI,CI005026.WI,CI005027.WI,CI005028.WI,CI005029.WI",
                 "pct_chg", begin_date, end_date, "")
    pct_data_pd = pd.DataFrame(data.Data, index=data.Codes, columns=data.Times).T
    pct_data_pd.index = pct_data_pd.index.map(lambda x: x.strftime('%Y-%m-%d'))
    pct_data_pd_cum = ((pct_data_pd / 100.0 + 1.0).cumprod() - 1.0).ix[len(pct_data_pd)-1,:]
    pct_data_pd_cum.name = 'pct'
    code_str = ','.join(list(pct_data_pd_cum.index))
    code_name = w.wss(code_str, "sec_name")
    code_name_pd = pd.DataFrame(code_name.Data, index=['name'], columns=data.Codes).T
    concat_data = pd.concat([pct_data_pd_cum, code_name_pd], axis=1)
    concat_data['name'] = concat_data['name'].map(lambda x: x[0:list(x).index('(')])
    concat_data = concat_data.sort_values(by=['pct'], ascending=False)
    concat_data_before = concat_data.iloc[0:3, :]
    concat_data_before['pct_str'] = concat_data_before['pct'].map(lambda x: ("%.2f%%") % (x*100))
    concat_data_before['out'] = concat_data_before['name'] + '行业(' + concat_data_before['pct_str'] + ')'
    concat_data = concat_data.sort_values(by=['pct'], ascending=True)
    concat_data_after = concat_data.iloc[0:3, :]
    concat_data_after['pct_str'] = concat_data_after['pct'].map(lambda x: ("%.2f%%") % (x*100))
    concat_data_after['out'] = concat_data_after['name'] + '行业(' + concat_data_after['pct_str'] + ')'
    return concat_data_before, concat_data_after


def load_fund_rank(fund_code, begin_date, end_date):

    data = w.wss(fund_code, "peer_fund_return_rank_per", "startDate=" + begin_date +
                 ";endDate=" + end_date + ";fundType=3")

    return data.Data[0][0]


def insert_para(doc, strContent, font="仿宋_GB2312", size=12, space=12, align=0):

    # 插入段
    p = doc.Paragraphs.Add()
    p.Range.Font.Name = font
    p.Range.Font.Size = size
    p.Range.ParagraphFormat.Alignment = align
    p.Range.ParagraphFormat.LineSpacing = space
    p.Range.InsertBefore(strContent)

    return True


def write_word_hs300(fund_name, fund_code, benchmark_code, index_code, mb_date, path):

    wordApp = win32com.client.Dispatch('Word.Application')
    wordApp.Visible = 0
    wordApp.DisplayAlerts = 0
    doc = wordApp.Documents.Add()
    print(fund_name)

    title = fund_name + '月报'

    insert_para(doc=doc, align=1, strContent=title, size=12, space=18)
    insert_para(doc=doc, align=0, strContent='（1）近期市场回顾', size=10, space=18)
    begin_date, end_date = get_date()
    half_year = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=183)).strftime('%Y-%m-%d')
    last_month, lastDay = get_last_month_last_date()
    pct, std = load_index_pct(index_code, begin_date, end_date)
    pct_half, std_half = load_index_pct(index_code, half_year, end_date)
    pe_ttm = load_index_pe(index_code, end_date)
    fund_pct, fund_std = load_fund_pct(fund_code, begin_date, end_date)
    fund_pct_half, fund_std_half = load_fund_pct(fund_code, half_year, end_date)
    bm_pct, bm_std = load_index_pct(benchmark_code, begin_date, end_date)
    ind_before, ind_after = load_three_industry(begin_date, end_date)
    rank = load_fund_rank(fund_code, begin_date, end_date)
    mg_fund_pct, mg_fund_std = load_fund_pct(fund_code, mb_date, end_date)
    mg_rank = load_fund_rank(fund_code, mb_date, end_date)
    mg_bm_pct, mg_bm_std = load_index_pct(benchmark_code, mb_date, end_date)

    para1 = '截至' + str(last_month) + '月' + str(lastDay) + '日，上月沪深300指数涨跌幅为' + format_number_to_pctstr(pct) + \
             "，近半年指数的年化波动率为" + format_number_to_pctstr(std_half) + '，指数期末动态市盈率为' + str(pe_ttm) + \
            "。上月涨幅最大的三个行业为" + ind_before.ix[0, "out"] + '，' + ind_before.ix[1, "out"] + \
             '和' + ind_before.ix[2, "out"] + "；上月跌幅最大的三个行业为" + ind_after.ix[0, "out"] + '，' + ind_after.ix[1, "out"] + \
             '和' + ind_after.ix[2, "out"] + '。'
    insert_para(doc=doc, align=0, strContent=para1, size=8, space=18)
    insert_para(doc=doc, align=0, strContent='（2）基金业绩表现', size=10, space=18)
    para2 = '截至' + str(last_month) + '月' + str(lastDay) + '日，上月' + fund_name + '基金涨跌幅为' + \
            format_number_to_pctstr(fund_pct) + "，最近半年本基金的年化波动率为" + format_number_to_pctstr(fund_std_half) + \
            '。' + fund_name + '基准涨跌幅为' + format_number_to_pctstr(bm_pct) + '，基金超额收益率为' + \
            format_number_to_pctstr(fund_pct - bm_pct) + '，同类排名为' + rank + '。现任基金经理管理以来(' + \
            mb_date + ")基金涨跌幅为" + format_number_to_pctstr(mg_fund_pct) + "，基金基准涨跌幅为" +  \
            format_number_to_pctstr(mg_bm_pct) + '，基金超额收益率为' + \
            format_number_to_pctstr(mg_fund_pct - mg_bm_pct) + '，同类排名为' + mg_rank + '。'

    insert_para(doc=doc, align=0, strContent=para2, size=8, space=18)
    insert_para(doc=doc, align=0, strContent='（3）投资展望', size=10, space=18)
    insert_para(doc=doc, align=0, strContent='待补充......', size=8, space=18)
    doc.SaveAs(path + fund_name + '月报.doc')

    doc.Close()
    wordApp.Quit()


def write_word_nxcl(fund_name, fund_code, benchmark_code, index_code, mb_date, path):

    wordApp = win32com.client.Dispatch('Word.Application')
    wordApp.Visible = 0
    wordApp.DisplayAlerts = 0
    doc = wordApp.Documents.Add()
    print(fund_name)

    title = fund_name + '月报'

    insert_para(doc=doc, align=1, strContent=title, size=12, space=18)
    insert_para(doc=doc, align=0, strContent='（1）近期市场回顾', size=10, space=18)
    begin_date, end_date = get_date()
    last_month, lastDay = get_last_month_last_date()
    half_year = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=183)).strftime('%Y-%m-%d')
    one_year = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=365)).strftime('%Y-%m-%d')
    three_year = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=365*3)).strftime('%Y-%m-%d')
    five_year = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=365*5)).strftime('%Y-%m-%d')

    pct, std = load_index_pct(index_code, begin_date, end_date)
    pct_half, std_half = load_index_pct(index_code, half_year, end_date)
    pe_ttm = load_index_pe(index_code, end_date)
    fund_pct, fund_std = load_fund_pct(fund_code, begin_date, end_date)
    fund_pct_half, fund_std_half = load_fund_pct(fund_code, half_year, end_date)
    ind_before, ind_after = load_three_industry(begin_date, end_date)
    one_rank = load_fund_rank(fund_code, one_year, end_date)
    three_rank = load_fund_rank(fund_code, three_year, end_date)
    five_rank = load_fund_rank(fund_code, five_year, end_date)

    mg_fund_pct, mg_fund_std = load_fund_pct(fund_code, mb_date, end_date)
    mg_rank = load_fund_rank(fund_code, mb_date, end_date)
    mg_bm_pct, mg_bm_std = load_index_pct(benchmark_code, mb_date, end_date)

    para1 = '截至' + str(last_month) + '月' + str(lastDay) + '日，上月沪深300指数涨跌幅为' + format_number_to_pctstr(pct) + \
             "，近半年指数的年化波动率为" + format_number_to_pctstr(std_half) + '，指数期末动态市盈率为' + str(pe_ttm) + \
            "。上月涨幅最大的三个行业为" + ind_before.ix[0, "out"] + '，' + ind_before.ix[1, "out"] + \
             '和' + ind_before.ix[2, "out"] + "；上月跌幅最大的三个行业为" + ind_after.ix[0, "out"] + '，' + ind_after.ix[1, "out"] + \
             '和' + ind_after.ix[2, "out"] + '。'
    insert_para(doc=doc, align=0, strContent=para1, size=8, space=18)
    insert_para(doc=doc, align=0, strContent='（2）基金业绩表现', size=10, space=18)
    para2 = '截至' + str(last_month) + '月' + str(lastDay) + '日，上月' + fund_name + '基金涨跌幅为' + \
            format_number_to_pctstr(fund_pct) + "，最近半年基金的年化波动率为" + format_number_to_pctstr(fund_std_half) + \
            '。' + '基金最近一年同类排名为' + one_rank + '，最近三年同类排名为' + \
            three_rank + '，最近五年同类排名为' + five_rank + '。现任基金经理管理以来(' + \
            mb_date + ")基金涨跌幅为" + format_number_to_pctstr(mg_fund_pct) + "，基金基准涨跌幅为" +  \
            format_number_to_pctstr(mg_bm_pct) + '，基金超额收益率为' + \
            format_number_to_pctstr(mg_fund_pct - mg_bm_pct) + '，同类排名为' + mg_rank + '。'

    insert_para(doc=doc, align=0, strContent=para2, size=8, space=18)
    insert_para(doc=doc, align=0, strContent='（3）投资展望', size=10, space=18)
    insert_para(doc=doc, align=0, strContent='待补充......', size=8, space=18)

    doc.SaveAs(path + fund_name + '月报.doc')

    doc.Close()
    wordApp.Quit()


def fund_month_report():

    ###########################################################################
    fund_name = '泰达宏利沪深300'
    fund_code = '162213.OF'
    benchmark_code = '162213BI.WI'
    index_code = "000300.SH"
    mb_date = '2014-10-13'
    path = 'E:\\3_数据\\7_other_data\\1_month_fund_report_doc\\'
    write_word_hs300(fund_name, fund_code, benchmark_code, index_code, mb_date, path)

    # 沪深300的基准收益有些不准
    ###########################################################################
    fund_name = '泰达宏利逆向策略'
    fund_code = '229002.OF'
    benchmark_code = '229002BI.WI'
    index_code = "000300.SH"
    mb_date = '2014-01-03'
    write_word_nxcl(fund_name, fund_code, benchmark_code, index_code, mb_date, path)
    ###########################################################################

if __name__ == '__main__':

    fund_month_report()
