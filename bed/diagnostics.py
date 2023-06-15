import logging
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt


def diagnostics(fake_param: int = 1, data=None):
    """Fake function to remove.

    :param fake_param:                          A fake integer
    :type fake_param:                           int
    :param data:                                Data read from config file paths
    :type data:                                 class

    :return:                                    boolean value

    """

    logging.info('This is a log file for diagnostics')

    # Plot Temperature Data
    logging.info('Plotting diagnostics for temperature data...')

    if data != None:
        ds = data.temperature
        ds.data_vars
        ds.T2.XTIME
        t2_cold = ds.T2.isel(Time=1)
        t2_hot = ds.T2.isel(Time=12)
        t2 = xr.concat([t2_cold, t2_hot], pd.Index(['Night', 'Day'], name='Cycle'))
        t2.values.shape
        t2.coords
        plot_t2 = t2.plot(x="west_east", y="south_north", col="Cycle")
        plt.show()
        # Save the plot into the diagnostics folder created by read_data()

    logging.info('Plotting diagnostics for temperature data complete.')


    return 'diagnostics'
