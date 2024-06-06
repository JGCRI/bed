import os
import logging
import pandas as pd
import xarray as xr
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


def diagnostics(input_data=None, degree_hours=None, demand=None, buildings=None, name='figure'):
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
    logging.info('Plotting diagnostics for input temperature data...')

    if input_data != None:
        # Temperature data
        ds = input_data.temperature.t2m

        # Plot
        ds.isel(time=1).plot()

        # Save the plot into the diagnostics folder created by read_data()
        plt.savefig(fname=os.path.join(input_data.dir_diagnostics, 'diagnostic_temperature.png'))
        plt.close()

    logging.info(f"Diagnostic plots saved to: {os.path.join(input_data.dir_diagnostics, 'diagnostic_temperature.png')}")
    logging.info('Plotting diagnostics for temperature data complete.')

    # Plot Degree Hour data
    logging.info('Plotting diagnostics for building properties data...')
    if buildings != None:
        area = buildings['area']
        height = buildings['height']
        floor = buildings['floor']
        s2far = buildings['s2far']
        
        # Plot
        fig, ((ax1, ax2),(ax3, ax4)) = plt.subplots(2,2, figsize=(15,10))

        area.plot(ax=ax1, norm=colors.SymLogNorm(linthresh=1e-2))
        height.plot(ax=ax2, norm=colors.SymLogNorm(linthresh=1e-2))
        floor.plot(ax=ax3, norm=colors.SymLogNorm(linthresh=1e-2))
        s2far.plot(ax=ax4, norm=colors.SymLogNorm(linthresh=1e-2))

        ax1.set_title('Building Area')
        ax2.set_title('Building Height')
        ax3.set_title('Floor Space')
        ax4.set_title('Surface to Floor Space Ratio')

        # Save the plot into the diagnostics folder created by read_data()
        plt.savefig(fname=os.path.join(input_data.dir_diagnostics, 'buildings.png'))
        plt.close()

        logging.info('Plotting diagnostics for building properties data complete.')

    # Plot Building Properties
    logging.info('Plotting diagnostics for degree hour data...')
    if degree_hours != None:
        hdd = degree_hours['hdd']
        cdd = degree_hours['cdd']
        
        # Plot
        fig, (ax1, ax2) = plt.subplots(1,2, figsize=(15,5))

        hdd.plot(ax=ax1)
        cdd.plot(ax=ax2)

        ax1.set_title('Heating Degree Hours')
        ax2.set_title('Cooling Degree Hours')

        # Save the plot into the diagnostics folder created by read_data()
        plt.savefig(fname=os.path.join(input_data.dir_diagnostics, 'hdd_cdd.png'))
        plt.close()

        logging.info('Plotting diagnostics for degree hour data complete.')

    # Plot Demand
    logging.info('Plotting diagnostics for demand data...')
    if demand != None:
        heating_demand = demand['demand_h']
        cooling_demand = demand['demand_c']
        
        # Plot
        fig, (ax1, ax2) = plt.subplots(1,2, figsize=(15,5))

        heating_demand.plot(ax=ax1, norm=colors.SymLogNorm(linthresh=1e-2))
        cooling_demand.plot(ax=ax2, norm=colors.SymLogNorm(linthresh=1e-2))

        ax1.set_title('Heating Demand')
        ax2.set_title('Cooling Demand')

        # Save the plot into the diagnostics folder created by read_data()
        plt.savefig(fname=os.path.join(input_data.dir_diagnostics, 'demand.png'))
        plt.close()

        logging.info('Plotting diagnostics for demand data complete.')

    ...
