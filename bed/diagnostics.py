import os
import logging
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt


def diagnostics(fake_param: int = 1, data=None, name='figure'):
    """Fake function to remove.

    :param fake_param:                          A fake integer
    :type fake_param:                           int
    :param data:                                Data read from config file paths
    :type data:                                 class
    :param name:                                name for the plot
    :type data:                                 str

    :return:                                    boolean value

    """

    # Plot Temperature Data
    logging.info('Plotting diagnostics for temperature data...')

    if data != None:
        ds = data.temperature
        ds.data_vars
        ds.T2.XTIME
        t2_1 = ds.T2.isel(Time=1)
        t2_2 = ds.T2.isel(Time=12)
        t2 = xr.concat([t2_1, t2_2], pd.Index([t2_1.XTIME.values.astype('str')[0:19], t2_2.XTIME.values.astype('str')[0:19]], name="T"))
        t2.values.shape
        t2.coords
        plot_t2 = t2.plot(x="west_east", y="south_north", col="T")
        plt.show()
        # Save the plot into the diagnostics folder created by read_data()
        plt.savefig(fname=os.path.join(data.dir_diagnostics, name + '.png'))

    logging.info(f"Diagnostic plots saved to: {os.path.join(data.dir_diagnostics, name + '.png')}")
    logging.info('Plotting diagnostics for temperature data complete.')


    return 'diagnostics'
