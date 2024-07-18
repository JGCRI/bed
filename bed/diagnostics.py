import os
import logging
from numpy import nansum
import pandas as pd
import xarray as xr
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cf


def diagnostics(input_data, demand, diag_out, calibration_coefficients):
    """Fake function to remove.

    :param fake_param:                          A fake integer
    :type fake_param:                           int
    :param data:                                Data read from config file paths
    :type data:                                 class
    :param name:                                name for the plot
    :type data:                                 str

    :return:                                    boolean value

    """

    # Plot Heating and Cooling Degree Hours
    plot_hdh_cdh(input_data, diag_out)

    # Plot Building Data
    plot_comm_buildings(input_data, diag_out)
    plot_resid_buildings(input_data, diag_out)

    # Plot demand
    plot_demand(input_data['base_year'], demand, diag_out)

    ...


def plot_temperature():
    ...


def plot_resid_buildings(input_data, diag_out):
    """
    Plotting buildings data for residential sector
    """
    logging.info('Plotting diagnostics for residential building data...')

    # Number of years estimated + base year
    n_inputs = len(input_data)

    # Set up figure
    fig, axes = plt.subplots(
        n_inputs, 5, figsize = (14, n_inputs*3),
        subplot_kw = {'projection': ccrs.PlateCarree()},
        gridspec_kw = {
            'wspace': 0.2, 
            'hspace': 0.01,
            'width_ratios': [1, 20, 20, 20, 20]
            },
        constrained_layout=True
    )

    # For each input setup plot HDD and CDD
    for i, (key, data) in enumerate(input_data.items()):
        # Get data
        area = data['resid_area']
        height = data['resid_height']
        floor_space = data['resid_floor_space']
        surface_to_floor_area_ratio = data['resid_surface_to_floor_area_ratio']

        # Plot them side by side by side by side
        area.plot(ax=axes[i,1], cbar_kwargs={'label': "sq meters"}, robust=True)
        height.plot(ax=axes[i,2], cbar_kwargs={'label': "meters"}, robust=True)
        floor_space.plot(ax=axes[i,3], cbar_kwargs={'label': "sq meters"}, robust=True)
        surface_to_floor_area_ratio.plot(ax=axes[i,4], cbar_kwargs={'label': "Ratio"}, robust=True)

        # Add coastlines and borders
        axes[i,1].coastlines()
        axes[i,1].add_feature(cf.BORDERS, linewidth=0.5, edgecolor='black')
        axes[i,2].coastlines()
        axes[i,2].add_feature(cf.BORDERS, linewidth=0.5, edgecolor='black')
        axes[i,3].coastlines()
        axes[i,3].add_feature(cf.BORDERS, linewidth=0.5, edgecolor='black')
        axes[i,4].coastlines()
        axes[i,4].add_feature(cf.BORDERS, linewidth=0.5, edgecolor='black')

        # Row name
        axes[i,0].axis('off')
        axes[i,0].text(x=0.5,y=0.5,s=data['year'])

    # Column names
    axes[0,1].set_title('Area')
    axes[0,2].set_title('Height')
    axes[0,3].set_title('Floor Space')
    axes[0,4].set_title('Surface to Floor Space Ratio')

    plt.savefig(fname=os.path.join(diag_out, 'resid_buildings.png'))
    plt.close()

    logging.info(f"Diagnostic plots saved to: {os.path.join(diag_out, 'resid_buildings.png')}")
    ...


def plot_comm_buildings(input_data, diag_out):
    """
    Plotting buildings data for residential sector
    """
    logging.info('Plotting diagnostics for non-residential building data...')

    # Number of years estimated + base year
    n_inputs = len(input_data)

    # Set up figure
    fig, axes = plt.subplots(
        n_inputs, 5, figsize = (14, n_inputs*3),
        subplot_kw = {'projection': ccrs.PlateCarree()},
        gridspec_kw = {
            'wspace': 0.2, 
            'hspace': 0.01,
            'width_ratios': [1, 20, 20, 20, 20]
            },
        constrained_layout=True
    )

    # For each input setup plot HDD and CDD
    for i, (key, data) in enumerate(input_data.items()):
        # Get data
        area = data['comm_area']
        height = data['comm_height']
        floor_space = data['comm_floor_space']
        surface_to_floor_area_ratio = data['comm_surface_to_floor_area_ratio']

        # Plot them side by side by side by side
        area.plot(ax=axes[i,1], cbar_kwargs={'label': "sq meters"}, robust=True)
        height.plot(ax=axes[i,2], cbar_kwargs={'label': "meters"}, robust=True)
        floor_space.plot(ax=axes[i,3], cbar_kwargs={'label': "sq meters"}, robust=True)
        surface_to_floor_area_ratio.plot(ax=axes[i,4], cbar_kwargs={'label': "Ratio"}, robust=True)

        # Add coastlines and borders
        axes[i,1].coastlines()
        axes[i,1].add_feature(cf.BORDERS, linewidth=0.5, edgecolor='black')
        axes[i,2].coastlines()
        axes[i,2].add_feature(cf.BORDERS, linewidth=0.5, edgecolor='black')
        axes[i,3].coastlines()
        axes[i,3].add_feature(cf.BORDERS, linewidth=0.5, edgecolor='black')
        axes[i,4].coastlines()
        axes[i,4].add_feature(cf.BORDERS, linewidth=0.5, edgecolor='black')

        # Row name
        axes[i,0].axis('off')
        axes[i,0].text(x=0.5,y=0.5,s=data['year'])

    # Column names
    axes[0,1].set_title('Area')
    axes[0,2].set_title('Height')
    axes[0,3].set_title('Floor Space')
    axes[0,4].set_title('Surface to Floor Space Ratio')

    plt.savefig(fname=os.path.join(diag_out, 'comm_buildings.png'))
    plt.close()

    logging.info(f"Diagnostic plots saved to: {os.path.join(diag_out, 'comm_buildings.png')}")
    ...


def plot_demand(input_data, demand, diag_out):
    """
    Plots final estimated energy demand for heating and cooling in residential and non-residential sectors
    for each year, including the base year demand used for calibration.
    """
    logging.info('Plotting heating and cooling demand...')

    # Number of years estimated + base year
    n_outputs = len(demand) + 1

    # Set up figure
    fig, axes = plt.subplots(
        n_outputs, 5, figsize = (15, n_outputs*3),
        subplot_kw = {'projection': ccrs.PlateCarree()},
        gridspec_kw = {
            'wspace': 0.2, 
            'hspace': 0.01,
            'width_ratios': [1, 20, 20, 20, 20]
            },
        constrained_layout=True
    )

    # For each input setup plot HDD and CDD
    for i, (key, data) in enumerate(demand.items()):
        # Get heating and cooling demand data
        resid_heating_demand = data['resid']['demand_h']
        resid_cooling_demand = data['resid']['demand_c']
        comm_heating_demand = data['comm']['demand_h']
        comm_cooling_demand = data['comm']['demand_c']

        # Plot them side by side
        resid_heating_demand.plot(ax=axes[i,1], cbar_kwargs={'label': "Demand per unit floor space"}, robust=True)
        resid_cooling_demand.plot(ax=axes[i,2], cbar_kwargs={'label': "Demand per unit floor space"}, robust=True)
        comm_heating_demand.plot(ax=axes[i,3], cbar_kwargs={'label': "Demand per unit floor space"}, robust=True)
        comm_cooling_demand.plot(ax=axes[i,4], cbar_kwargs={'label': "Demand per unit floor space"}, robust=True)

        # Add coastlines and borders
        axes[i,1].coastlines()
        axes[i,1].add_feature(cf.BORDERS, linewidth=0.5, edgecolor='black')
        axes[i,2].coastlines()
        axes[i,2].add_feature(cf.BORDERS, linewidth=0.5, edgecolor='black')
        axes[i,3].coastlines()
        axes[i,3].add_feature(cf.BORDERS, linewidth=0.5, edgecolor='black')
        axes[i,4].coastlines()
        axes[i,4].add_feature(cf.BORDERS, linewidth=0.5, edgecolor='black')

        # Row name
        axes[i,0].axis('off')
        axes[i,0].text(x=0.5,y=0.5,s=key)

    # Plot base year demand
    # Convert total demand to demand per unit floor-space
    resid_fs_times_hdd = input_data['resid_floor_space'] * input_data['degree_hours']['hdd']
    resid_fs_times_cdd = input_data['resid_floor_space'] * input_data['degree_hours']['cdd']
    comm_fs_times_hdd = input_data['comm_floor_space'] * input_data['degree_hours']['hdd']
    comm_fs_times_cdd = input_data['comm_floor_space'] * input_data['degree_hours']['cdd']
    # TODO: Normalize bracketed term ?
    resid_heating_demand = input_data['resid_heating_demand'] * (resid_fs_times_hdd / nansum(resid_fs_times_hdd.data) / input_data['resid_floor_space'])
    resid_cooling_demand = input_data['resid_cooling_demand'] * (resid_fs_times_cdd / nansum(resid_fs_times_cdd.data) / input_data['resid_floor_space'])
    comm_heating_demand = input_data['comm_heating_demand'] * (comm_fs_times_hdd / nansum(comm_fs_times_hdd.data) / input_data['comm_floor_space'])
    comm_cooling_demand = input_data['comm_cooling_demand'] * (comm_fs_times_cdd / nansum(comm_fs_times_cdd.data) / input_data['comm_floor_space'])

    # Plot them side by side
    resid_heating_demand.plot(ax=axes[(n_outputs-1),1], cbar_kwargs={'label': "Demand per unit floor space"}, robust=True)
    resid_cooling_demand.plot(ax=axes[(n_outputs-1),2], cbar_kwargs={'label': "Demand per unit floor space"}, robust=True)
    comm_heating_demand.plot(ax=axes[(n_outputs-1),3], cbar_kwargs={'label': "Demand per unit floor space"}, robust=True)
    comm_cooling_demand.plot(ax=axes[(n_outputs-1),4], cbar_kwargs={'label': "Demand per unit floor space"}, robust=True)

    # Add coastlines and borders
    axes[(n_outputs-1),1].coastlines()
    axes[(n_outputs-1),1].add_feature(cf.BORDERS, linewidth=0.5, edgecolor='black')
    axes[(n_outputs-1),2].coastlines()
    axes[(n_outputs-1),2].add_feature(cf.BORDERS, linewidth=0.5, edgecolor='black')
    axes[(n_outputs-1),3].coastlines()
    axes[(n_outputs-1),3].add_feature(cf.BORDERS, linewidth=0.5, edgecolor='black')
    axes[(n_outputs-1),4].coastlines()
    axes[(n_outputs-1),4].add_feature(cf.BORDERS, linewidth=0.5, edgecolor='black')

    # Row name
    axes[(n_outputs-1),0].axis('off')
    axes[(n_outputs-1),0].text(x=0.5,y=0.5,s=input_data['year'])

    # Column names
    axes[0,1].set_title('Residential Heating Demand')
    axes[0,2].set_title('Residential Cooling Demand')
    axes[0,3].set_title('Non-Residential Heating Demand')
    axes[0,4].set_title('Non-Residential Cooling Demand')

    plt.savefig(fname=os.path.join(diag_out, 'demand.png'))
    plt.close()

    logging.info(f"Diagnostic plots saved to: {os.path.join(diag_out, 'demand.png')}")
    ...


def plot_demand_year():
    ...


def plot_calibration():
    ...


def plot_hdh_cdh(input_data, diag_out):
    """
    Plotting Heating and Cooling Degree Days
    """
    logging.info('Plotting diagnostics for HDD & CDD...')

    # Number of years estimated + base year
    n_inputs = len(input_data)

    # Set up figure
    fig, axes = plt.subplots(
        n_inputs, 3, figsize = (10, n_inputs*3),
        subplot_kw = {'projection': ccrs.PlateCarree()},
        gridspec_kw = {
            'wspace': 0.2, 
            'hspace': 0.01,
            'width_ratios': [1, 20, 20]
            },
        constrained_layout=True
    )

    # For each input setup plot HDD and CDD
    for i, (key, data) in enumerate(input_data.items()):
        # Get HDD and CDD data
        hdd = data['degree_hours']['hdd']
        cdd = data['degree_hours']['cdd']

        # Plot them side by side
        hdd.plot(ax=axes[i,1], cbar_kwargs={'label': "°Hours"}, robust=True)
        cdd.plot(ax=axes[i,2], cbar_kwargs={'label': "°Hours"}, robust=True)

        # Add coastlines and borders
        axes[i,1].coastlines()
        axes[i,1].add_feature(cf.BORDERS, linewidth=0.5, edgecolor='black')
        axes[i,2].coastlines()
        axes[i,2].add_feature(cf.BORDERS, linewidth=0.5, edgecolor='black')

        # Row name
        axes[i,0].axis('off')
        axes[i,0].text(x=0.5,y=0.5,s=key)

    # Column names
    axes[0,1].set_title('Heating Degree Hours')
    axes[0,2].set_title('Cooling Degree Hours')

    plt.savefig(fname=os.path.join(diag_out, 'hdh_cdh.png'))
    plt.close()

    logging.info(f"Diagnostic plots saved to: {os.path.join(diag_out, 'hdh_cdh.png')}")
    ...