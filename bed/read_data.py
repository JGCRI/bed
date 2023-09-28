import logging
import pandas as pd
import xarray as xr
import numpy as np
import os as os
import xesmf as xe
from bed.read_config import read_config

# Inputs needed:
#   k unitless calibration coefficient
#   HDH heating degree hours
#   CDH cooling degree hours
#   n = thermal conductance (GJ/m2 hour C)
#   R = unitless average surface-to-floor area ratio
#   IG internal gain [GJ/m2]
#   uh = region and sector-specific demand satition for heating
#   uc = region and sector-specific demand satition for cooling
#   i = per-capita income
#   Ph = total price of service (weighted average of technologies used) heating
#   Pc = total price of service (weighted average of technologies used) cooling


class Data:
    """ Data class"""

    def __init__(self, config_file=''):
        """
        :param config_file:         configuration file path
        :type config_file:          string
        :return:               Data
        """

        logging.info('Starting class Data inside module read_data...')

        self.config = read_config(config_file=config_file)

        if self.config != '':

            # Create folders for outputs in same location as config
            self.dir_root = os.path.dirname(os.path.abspath(config_file))
            self.dir_outputs = os.path.abspath(os.path.join(self.dir_root, self.config['dir_outputs']))
            self.dir_diagnostics = os.path.abspath(os.path.join(self.dir_outputs, "diagnostics"))

            if not os.path.exists(self.dir_outputs):
                logging.info(f'Creating: {self.dir_outputs}')
                os.makedirs(self.dir_outputs, exist_ok=True)

            if not os.path.exists(self.dir_diagnostics):
                logging.info(f'Creating: {self.dir_diagnostics}')
                os.makedirs(self.dir_diagnostics, exist_ok=True)

            # Read datasets
            # Assume datasets are in same folder as config_file
            if os.path.exists(os.path.abspath(os.path.join(self.dir_root, self.config['path_example_data_set']))):
                self.example_dataset = pd.read_csv(os.path.abspath(os.path.join(self.dir_root, self.config['path_example_data_set'])))
            else: # If user gives full path
                self.example_dataset = pd.read_csv(os.path.abspath(self.config['path_example_data_set']))

            if os.path.exists(os.path.abspath(os.path.join(self.dir_root, self.config['path_temperature_ncdf']))):
                self.temperature = xr.open_dataset(os.path.abspath(os.path.join(self.dir_root, self.config['path_temperature_ncdf'])))
            else: # If user gives full path
                self.temperature = xr.open_dataset(self.config['path_temperature_ncdf'])

            if os.path.exists(os.path.abspath(os.path.join(self.dir_root, self.config['path_population_ncdf']))):
                self.population = xr.open_dataset(os.path.abspath(os.path.join(self.dir_root, self.config['path_population_ncdf'])))
            else: # If user gives full path
                self.population = xr.open_dataset(self.config['path_population_ncdf'])

        # Regrid each data


        logging.info('Class Data inside module read_data completed.')



    @staticmethod
    def set_global_coords(resolution):

        offset = resolution / 2

        coords = xr.Dataset({
            "lat": (["lat"], np.linspace(90 - offset, -90 + offset, round(180 / resolution)), {"units": "degrees_north"}),
            "lon": (["lon"], np.linspace(-180 + offset, 180 - offset, round(360 / resolution)), {"units": "degrees_east"}),
        })

        return coords

    def regrid(self, ds, target_resolution, method='conservative'):
        """Simple regridding algorithm

        :param ds: xarray Dataset or DataArray, needs lat and lon and global extent
        :param target_resolution: target resolution in degrees
        :param method: choice of 'extensive' (preserves sums, default), 'intensive' (take average), or 'label' (for maps)
        :return: ds regridded to target_resolution
        """

        # Set target coordinates
        ds_out = self.set_global_coords(target_resolution)


        # Perform regridding
        regridder = xe.Regridder(ds, ds_out, method)

        # Regrid with a Data Array
        da = ds['ssp2_2020']
        da = da.transpose('lat', 'lon')
        ds_out = regridder(da)



        return ds_out

