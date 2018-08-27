from quant.project.stock_project.barra_risk_model.barra_factor.cal_factor_barra_beta import cal_factor_barra_beta
from quant.project.stock_project.barra_risk_model.barra_factor.cal_factor_barra_nolinear_size import cal_factor_barra_nonlinear_size
from quant.project.stock_project.barra_risk_model.barra_factor.cal_factor_barra_size import cal_factor_barra_size
from quant.project.stock_project.barra_risk_model.barra_factor.cal_factor_barra_book_to_price import cal_factor_barra_book_to_price
from quant.project.stock_project.barra_risk_model.barra_factor.cal_factor_barra_momentum import cal_factor_barra_momentum
from quant.project.stock_project.barra_risk_model.barra_factor.cal_factor_barra_earning_yield import cal_earning_yield
from quant.project.stock_project.barra_risk_model.barra_factor.cal_factor_barra_growth import cal_factor_barra_growth
from quant.project.stock_project.barra_risk_model.barra_factor.cal_factor_barra_leverage import cal_factor_barra_leverage
from quant.project.stock_project.barra_risk_model.barra_factor.cal_factor_barra_liquidity import cal_factor_liquidity
from quant.project.stock_project.barra_risk_model.barra_factor.cal_factor_Long_Term_ROE import cal_factor_Long_Term_ROE
from quant.project.stock_project.barra_risk_model.barra_factor.cal_factor_barra_residual_volatility import cal_factor_barra_residual_volatility

from datetime import datetime


def Barra_Risk_Model_Main():

    print("############################# 开始更新 Barra Risk Model ####################################")
    beg_date = '2018-01-01'
    end_date = datetime.today()

    cal_factor_barra_size(beg_date, end_date)
    cal_factor_barra_book_to_price(beg_date, end_date)
    cal_factor_barra_beta(beg_date, end_date)
    cal_factor_liquidity()
    cal_factor_barra_nonlinear_size(beg_date, end_date)
    cal_factor_barra_momentum(beg_date, end_date)

    # cal_factor_barra_residual_volatility()
    # cal_factor_Long_Term_ROE()
    # cal_factor_barra_leverage()
    # cal_earning_yield()
    # cal_factor_barra_growth()

    print("############################# 结束更新 Barra Risk Model ####################################")


if __name__ == '__main__':

    Barra_Risk_Model_Main()
