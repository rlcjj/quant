from quant.project.my_timer.quarter.fund_holding.update_fund_pool import fund_pool_update
from quant.project.my_timer.quarter.fund_holding.weight_allstock_halfyear_good import weight_all_stock_good_date
from quant.project.my_timer.quarter.fund_holding.weight_allstock_halfyear_holding import weight_allstock_holding_date
from quant.project.my_timer.quarter.fund_holding.equal_halfyear_holding import equal_allstock_halfyear_date
from quant.project.my_timer.quarter.fund_holding.equal_top10stock_holding import equal_top10stock_holding_date
from quant.project.my_timer.quarter.fund_holding.weight_top10stock_good import weight_top10stock_good_date
from quant.project.my_timer.quarter.fund_holding.weight_top10stock_holding import weight_top10stock_holding_date
from quant.project.my_timer.quarter.fund_holding.test_last_date import test_fund_position_update
from quant.fund.fund import Fund
from datetime import datetime


def fund_holding_update():

    print("##########    参数    ###############")
    date = '20180630'
    last_date = "20180331"

    print("########## 更新股票池 基金规模 基金持仓股票 ###############")
    Fund().load_wind_fund_asset(date)
    fund_pool_update(date)

    Fund().load_fund_holding("19991231", datetime.today())

    print("########## 检查持仓更新情况 ###############")
    test_fund_position_update(last_date)
    test_fund_position_update(date)

    print("########## 计算加权基金基准 ###############")
    weight_all_stock_good_date(date)
    weight_allstock_holding_date(date)
    equal_allstock_halfyear_date(date)
    equal_top10stock_holding_date(date)
    weight_top10stock_good_date(date)
    weight_top10stock_holding_date(date)

if __name__ == '__main__':

    fund_holding_update()
