from quant.fund.fund import Fund


def test_fund_position_update(date):

    data = Fund().get_fund_holding_all()
    report_date_list = list(set(data['Date'].values))
    report_date_list.sort()

    data_report = data[data['Date'] == date]
    fund_list = list(set(data_report['FundCode'].values))
    fund_list.sort()
    i = 0

    for fund_code in fund_list:
        data_fund = data_report[data_report['FundCode'] == fund_code]
        if len(data_fund) > 10:
            i += 1

    print("在 " + date + " 有" + str(len(fund_list)) + "只基金更新持仓")
    print("其中持仓超过10只的基金组合有", str(i) + "只")

if __name__ == '__main__':

    date = '20180630'
    test_fund_position_update(date)
    date = '20180331'
    test_fund_position_update(date)
