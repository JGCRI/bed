import os
import logging
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


def diagnostics(data=None, name='figure'):
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
        # Temperature data
        ds = data.temperature.t2m

        # Plot
        ds.isel(time=1).plot()

        # Save the plot into the diagnostics folder created by read_data()
        plt.savefig(fname=os.path.join(data.dir_diagnostics, 'diagnostic_temperature.png'))
        plt.close()

    logging.info(f"Diagnostic plots saved to: {os.path.join(data.dir_diagnostics, 'diagnostic_temperature.png')}")
    logging.info('Plotting diagnostics for temperature data complete.')

    # Plot Population Data
    logging.info('Plotting diagnostics for temperature data...')

    ...
