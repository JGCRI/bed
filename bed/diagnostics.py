import os
import logging
import pandas as pd
import xarray as xr
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


def diagnostics(input_data, demand, diag_out):
    """Fake function to remove.

    :param fake_param:                          A fake integer
    :type fake_param:                           int
    :param data:                                Data read from config file paths
    :type data:                                 class
    :param name:                                name for the plot
    :type data:                                 str

    :return:                                    boolean value

    """

    # Number of input / output setups
    n_inputs = len(input_data)
    n_outputs = n_inputs - 1

    # Plot Temperature Data ---------------------------
    logging.info('Plotting diagnostics for HDD & CDD...')

    # Set up figure
    fig, axes = plt.subplots(n_inputs, 2, figsize = (10, n_inputs*3))
    fig.tight_layout()
    # For each input setup plot HDD and CDD
    for i, (key, data) in enumerate(input_data.items()):
        # Get HDD and CDD data
        hdd = data['degree_hours']['hdd']
        cdd = data['degree_hours']['cdd']

        # Plot them side by side
        hdd.plot(ax=axes[i,0])
        cdd.plot(ax=axes[i,1])

        # Row name
        axes[i,0].annotate(key, xy=(0,0.5), ha='right', va='center')

    # Column names
    axes[0,0].set_title('HDD')
    axes[0,1].set_title('CDD')

    plt.savefig(fname=os.path.join(diag_out, 'hdd_cdd.png'))
    plt.close()

    logging.info(f"Diagnostic plots saved to: {os.path.join(diag_out, 'hdd_cdd.png')}")


    # Plot Building Properties ---------------------------
    logging.info('Plotting diagnostics for building data...')

    # Set up figure
    fig, axes = plt.subplots(n_inputs, 4, figsize = (18, n_inputs*3))
    fig.tight_layout()
    # For each input setup plot HDD and CDD
    for i, (key, data) in enumerate(input_data.items()):
        # Get data
        area = data['area']
        height = data['height']
        floor_space = data['floor_space']
        surface_to_floor_area_ratio = data['surface_to_floor_area_ratio']

        # Plot them side by side by side by side
        area.plot(ax=axes[i,0])
        height.plot(ax=axes[i,1])
        floor_space.plot(ax=axes[i,2])
        surface_to_floor_area_ratio.plot(ax=axes[i,3])

        # Row name
        axes[i,0].annotate(key, xy=(0,0.5), ha='right', va='center')

    # Column names
    axes[0,0].set_title('Area')
    axes[0,1].set_title('Height')
    axes[0,2].set_title('Floor Space')
    axes[0,3].set_title('Ratio')

    plt.savefig(fname=os.path.join(diag_out, 'buildings.png'))
    plt.close()

    logging.info(f"Diagnostic plots saved to: {os.path.join(diag_out, 'buildings.png')}")


    # Plot Demand Data ---------------------------
    logging.info('Plotting heating and cooling demand...')

    # Set up figure
    fig, axes = plt.subplots(n_outputs, 2, figsize = (9, n_outputs*3))
    fig.tight_layout()
    # For each input setup plot HDD and CDD
    for i, (key, data) in enumerate(demand.items()):
        # Get heating and cooling demand data
        heating_demand = data['demand_h']
        cooling_demand = data['demand_c']

        # Plot them side by side
        heating_demand.plot(ax=axes[i,0], norm=colors.SymLogNorm(linthresh=1e0))
        cooling_demand.plot(ax=axes[i,1], norm=colors.SymLogNorm(linthresh=1e0))

        # Row name
        axes[i,0].annotate(key, xy=(0,0.5), ha='right', va='center')

    # Column names
    axes[0,0].set_title('Heating Demand')
    axes[0,1].set_title('Cooling Demand')

    plt.savefig(fname=os.path.join(diag_out, 'demand.png'))
    plt.close()

    logging.info(f"Diagnostic plots saved to: {os.path.join(diag_out, 'demand.png')}")

    ...
