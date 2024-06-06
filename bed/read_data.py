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

            # Read spatial datasets
            self.temperature = self.read_spatial_data('temperature_data')
            self.building_area = self.read_spatial_data('building_area_data')
            self.building_height = self.read_spatial_data('building_height_data')
            self.income_per_capita = self.read_spatial_data('income_per_capita')
            self.income_per_capita = self.income_per_capita['income']

            # Read spatial datasets (base year)
            self.base_year_temperature = self.read_spatial_data('base_year_temperature_data')
            self.base_year_building_area = self.read_spatial_data('base_year_building_area_data')
            self.base_year_building_height = self.read_spatial_data('base_year_building_height_data')
            self.base_year_income_per_capita = self.read_spatial_data('base_year_income_per_capita')
            self.base_year_income_per_capita = self.base_year_income_per_capita['income']

            # Align, removes floating point errors of lat/lon alignment
            self.temperature, self.building_area, self.building_height = xr.align(self.temperature, self.building_area, self.building_height, join='override')
            self.base_year_temperature, self.base_year_building_area, self.base_year_building_height = xr.align(self.base_year_temperature, self.base_year_building_area, self.base_year_building_height, join='override')

            # Surface to floor ratio
            self.surface_to_floor_area_ratio, self.base_year_surface_to_floor_area_ratio = self.get_surface_to_floor_area_ratio()


        logging.info('Class Data inside module read_data completed.')

        ...

    def get_surface_to_floor_area_ratio(self):
        """
        Calculate surface to floor area ratio using building area and building height
        """
        logging.info('Calculating surface area to floor space ratio')

        # Formatting
        self.building_area = self.building_area['band_data'].squeeze('band').drop_vars(['band', 'spatial_ref']).transpose('y', 'x')
        self.building_height = self.building_height['band_data'].squeeze('band').drop_vars(['band', 'spatial_ref']).transpose('y', 'x')
        self.base_year_building_area = self.base_year_building_area['band_data'].squeeze('band').drop_vars(['band', 'spatial_ref']).transpose('y', 'x')
        self.base_year_building_height = self.base_year_building_height['band_data'].squeeze('band').drop_vars(['band', 'spatial_ref']).transpose('y', 'x')

        # Floor space
        self.floor_space = self.building_area * self.building_height / 3
        self.base_year_floor_space = self.base_year_building_area * self.base_year_building_height / 3
        self.total_floor_space = np.nansum(self.floor_space.data)
        self.base_year_total_floor_space = np.nansum(self.base_year_floor_space.data)

        # Length and Width assuming square building
        lw = np.sqrt(self.building_area)
        base_year_lw = np.sqrt(self.base_year_building_area)

        # Surface area, 4 sides + roof
        surface_area = (4 * (lw * self.building_height)) + (lw * lw)
        base_year_surface_area = (4 * (base_year_lw * self.base_year_building_height)) + (base_year_lw * base_year_lw)

        # Surface to floor area ratio
        s2far = surface_area / self.floor_space
        base_year_s2far = base_year_surface_area / self.base_year_floor_space

        return s2far, base_year_s2far

    def read_spatial_data(self, key):
        """
        Read in spatial datasets using Xarray

        :param key:         Key of in config file for path to data to read
        :type key:          string
        :return:            Xarray DataSet
        """

        logging.info(f'Reading {key} data')

        # Assume datasets are in same folder as config_file
        if os.path.exists(os.path.abspath(os.path.join(self.dir_root, self.config[key]))):
            spatial_data = xr.open_mfdataset(os.path.abspath(os.path.join(self.dir_root, self.config[key])))
        else: # If user gives full path
            spatial_data = xr.open_mfdataset(os.path.abspath(self.config[key]))
        
        return spatial_data

