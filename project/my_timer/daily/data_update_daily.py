from quant.stock.barra import Barra


def update_data_daily():

    """
    update barra
    """

    Barra().load_barra()

if __name__ == "__main__":

    update_data_daily()
