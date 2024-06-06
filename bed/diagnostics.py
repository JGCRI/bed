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
        ds = data.temperature
        # ds.data_vars
        # ds.T2.XTIME
        t2_1 = ds.T2.isel(Time=1)
        t2_2 = ds.T2.isel(Time=12)
        t2 = xr.concat([t2_1, t2_2], pd.Index([t2_1.XTIME.values.astype('str')[0:19], t2_2.XTIME.values.astype('str')[0:19]], name="T"))
        # t2.values.shape
        # t2.coords

        t2.plot(x="west_east", y="south_north", col="T")
        # plt.show()
        # Save the plot into the diagnostics folder created by read_data()
        plt.savefig(fname=os.path.join(data.dir_diagnostics, 'diagnostic_temperature.png'))
        plt.close()

    logging.info(f"Diagnostic plots saved to: {os.path.join(data.dir_diagnostics, 'diagnostic_temperature.png')}")
    logging.info('Plotting diagnostics for temperature data complete.')

    # Plot Population Data
    logging.info('Plotting diagnostics for temperature data...')

    if data != None:
        ds = data.population

        ticks = [0, 1000, 5000, 10000, 50000, 100000, 500000, 1000000, 5000000]
        subplot_kws = dict(projection=ccrs.PlateCarree(),
                           facecolor='white')

        plt.figure(figsize=[10, 5])
        p = ds.ssp2_2020.plot(x='lon', y='lat',
                              vmin=0, vmax=5000000,
                              size=4,
                              aspect=ds.dims['lon']/ds.dims['lat'],
                              cmap='viridis',
                              subplot_kws=subplot_kws,
                              transform=ccrs.PlateCarree(),
                              add_labels=False,
                              add_colorbar=False,
                              levels=ticks)

        cb = plt.colorbar(p, shrink=0.7, ticks=ticks)
        cb.ax.tick_params(labelsize=14)
        # plt.show()
        # Save the plot into the diagnostics folder created by read_data()
        plt.savefig(fname=os.path.join(data.dir_diagnostics, 'diagnostic_population.png'))
        plt.close()

    logging.info(f"Diagnostic plots saved to: {os.path.join(data.dir_diagnostics, 'diagnostic_population.png')}")
    logging.info('Plotting diagnostics for temperature data complete.')


    return 'diagnostics'
