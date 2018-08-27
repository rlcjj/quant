from quant.fund.fund_static import FundStatic
from quant.fund.fund_pool import FundPool
from quant.fund.fund_holder import FundHolder
from quant.fund.fund_factor import FundFactor
from quant.fund.fund_exposure import FundExposure


class Fund(FundStatic, FundPool, FundHolder, FundFactor, FundExposure):

    """
    继承多个Fund Class
    FundStatic()
    FundPool()
    FundHolder()
    FundFactor()
    """

    def __init__(self):

        FundHolder.__init__(self)
        FundFactor.__init__(self)
        FundPool.__init__(self)
        FundStatic.__init__(self)
        FundExposure.__init__(self)


if __name__ == "__main__":

    Fund().load_fund_info()
    print(Fund().get_fund_holding_report_date())
    print(Fund().get_fund_factor("Repair_Nav"))
    print(Fund().get_wind_fund_asset())
    print(Fund().get_fund_pool_name())
