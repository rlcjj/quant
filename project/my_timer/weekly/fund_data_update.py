from datetime import datetime
from quant.fund.fund import Fund
from quant.stock.date import Date


def load_fund_data_update():

    # 更新开始和结束时间
    Date().load_trade_date_series()
    end_date = Date().change_to_str(datetime.today())
    beg_date = Date().get_trade_date_offset(end_date, -30)
    quarter_beg_data = Date().get_trade_date_offset(end_date, -70)
    print(beg_date, end_date)

    # 基金基本情况和股票基本情况
    Fund().load_sec_info()
    Fund().load_fund_info()

    # 净值数据
    Fund().load_fund_factor("Unit_Nav", beg_date, end_date)
    Fund().load_fund_factor("Repair_Nav", beg_date, end_date)
    Fund().load_fund_factor("Repair_Nav_Pct", beg_date, end_date)
    Fund().load_fund_factor("Acc_Nav", beg_date, end_date)

    Fund().load_fund_factor("Total_Asset", quarter_beg_data, end_date)
    Fund().load_fund_factor("Stock_Ratio", quarter_beg_data, end_date)
    Fund().load_fund_factor("Fixed_Ratio", quarter_beg_data, end_date)

if __name__ == '__main__':

    load_fund_data_update()
