import logging
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt


def diagnostics(fake_param: int = 1):
    """Fake function to remove.

    :param fake_param:                          A fake integer
    :type fake_param:                           int

    :return:                                    boolean value

    """

    logging.info('This is a log file for diagnostics')

    # Read a xarray
    # ds = xr.open_dataset(r'C:\WorkSpace\LCLUC-Morocco\wrfout_d03_2014-08-09_Morocco_2014.nc')
    # ds
    #
    # ds.data_vars
    #
    # ds.T2.XTIME
    #
    # t2_cold = ds.T2.isel(Time=1)
    # t2_hot = ds.T2.isel(Time=12)
    #
    # t2 = xr.concat([t2_cold, t2_hot], pd.Index(['Night', 'Day'], name='Cycle'))
    # t2.values.shape
    # t2.coords
    #
    # t2.plot(x="west_east", y="south_north", col="Time")
    # plt.show()

    # Choose type of aggregation of the data

    # Choose time slot to plot (user can define the time as well)



    return 'diagnostics'
