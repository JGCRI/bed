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

        self.data_dict = {}

        if self.config != '':

            # Create folders for outputs in same location as config
            self.dir_root = os.path.dirname(os.path.abspath(config_file))
            self.dir_outputs = os.path.abspath(os.path.join(self.dir_root, self.config['dir_outputs']))
            self.dir_diagnostics = os.path.abspath(os.path.join(self.dir_outputs, "diagnostics"))

            # Threshold for area of cells covered by buildings
            coverage_percent_threshold = float(self.config['coverage_percent_threshold'])
            coverage_percent_conversion_factor = float(self.config['coverage_percent_conversion_factor'])

            # Coverage data
            self.resid_coverage_percent_mask = self.make_coverage_percent_mask('RES_base_year_building_area_data', coverage_percent_threshold, coverage_percent_conversion_factor)
            self.comm_coverage_percent_mask = self.make_coverage_percent_mask('NRES_base_year_building_area_data', coverage_percent_threshold, coverage_percent_conversion_factor)

            # Get base year data and shared data
            self.data_dict['base_year'] = self.get_base_year_data()

            # Get data for each year
            for key, data in self.config['years'].items():
                self.data_dict[key] = self.get_year_data(data)

        logging.info('Class Data inside module read_data completed.')

        ...

    def make_coverage_percent_mask(self, area_data_key, thresh, scale_factor):
        """
        Create a mask to keep cells which exceed the threshold for coverage percent
        """
        # Read area data
        building_area = self.read_spatial_data(area_data_key, self.config)
        building_area = building_area.squeeze('band').drop_vars(['band', 'spatial_ref']).transpose('y', 'x')['band_data']

        # Convert to percent coverage in each cell
        coverage_percent = building_area * scale_factor

        # Mask
        coverage_percent_mask = coverage_percent.where(coverage_percent > thresh)

        return coverage_percent_mask

    def get_base_year_data(self):
        """
        Read in data for the calibration year, or data that is shared between years
        """
        # Read spatial datasets (base year)
        base_year_temperature = self.read_spatial_data('base_year_temperature_data', self.config)
        resid_base_year_building_area = self.read_spatial_data('RES_base_year_building_area_data', self.config, mask=self.resid_coverage_percent_mask)
        comm_base_year_building_area = self.read_spatial_data('NRES_base_year_building_area_data', self.config, mask=self.comm_coverage_percent_mask)
        base_year_building_height = self.read_spatial_data('base_year_building_height_data', self.config)
        base_year_income_per_capita = self.read_spatial_data('base_year_income_per_capita', self.config)
        base_year_income_per_capita = base_year_income_per_capita['income']

        # Read shared spatial datasets
        resid_u_factor = self.read_spatial_data('RES_u_factor_data', self.config)
        comm_u_factor = self.read_spatial_data('NRES_u_factor_data', self.config)
        resid_u_factor = resid_u_factor['resid-u-factor']
        comm_u_factor = comm_u_factor['comm-u-factor']

        # Align spatial datasets
        base_year_temperature, \
        resid_base_year_building_area, \
        comm_base_year_building_area, \
        base_year_building_height, \
        base_year_income_per_capita, \
        resid_u_factor, \
        comm_u_factor = xr.align(base_year_temperature, 
                                 resid_base_year_building_area,
                                 comm_base_year_building_area, 
                                 base_year_building_height, 
                                 base_year_income_per_capita,
                                 resid_u_factor,
                                 comm_u_factor,
                                 join='override')

        # Surface to floor ratio
        resid_surface_to_floor_area_ratio, resid_floor_space, resid_total_floor_space, resid_base_year_building_area, resid_base_year_building_height = self.get_surface_to_floor_area_ratio(resid_base_year_building_area, base_year_building_height)
        comm_surface_to_floor_area_ratio, comm_floor_space, comm_total_floor_space, comm_base_year_building_area, comm_base_year_building_height = self.get_surface_to_floor_area_ratio(comm_base_year_building_area, base_year_building_height)

        # Return data in dictionary including constants
        return {
            'temperature': base_year_temperature,
            'resid_area': resid_base_year_building_area,
            'comm_area': comm_base_year_building_area,
            'resid_height': resid_base_year_building_height,
            'comm_height': comm_base_year_building_height,
            'income': base_year_income_per_capita,
            'resid_u_factor': resid_u_factor,
            'comm_u_factor': comm_u_factor,
            'resid_surface_to_floor_area_ratio': resid_surface_to_floor_area_ratio,
            'comm_surface_to_floor_area_ratio': comm_surface_to_floor_area_ratio,
            'resid_floor_space': resid_floor_space,
            'comm_floor_space': comm_floor_space,
            'resid_total_floor_space': resid_total_floor_space,
            'comm_total_floor_space': comm_total_floor_space,
            'year': int(self.config['base_year']),
            'coverage_percent_threshold': float(self.config['coverage_percent_threshold']),
            'temperature_variable_name': self.config['temperature_variable_name'],
            'temperature_units': self.config['temperature_units'],
            'comfortable_temperature_lower': float(self.config['comfortable_temperature_lower']),
            'comfortable_temperature_upper': float(self.config['comfortable_temperature_upper']),
            'u_factor_target_year': int(self.config['u_factor_target_year']),
            'u_factor_improvement_rate': float(self.config['u_factor_improvement_rate']),
            'resid_heating_demand': float(self.config['RES_base_year_heating_demand']),
            'resid_cooling_demand': float(self.config['RES_base_year_cooling_demand']),
            'comm_heating_demand': float(self.config['NRES_base_year_heating_demand']),
            'comm_cooling_demand': float(self.config['NRES_base_year_cooling_demand']),
            'satiation_factor': float(self.config['base_year_satiation_factor']),
            'resid_total_internal_gain': float(self.config['RES_base_year_total_internal_gain']),
            'comm_total_internal_gain': float(self.config['NRES_base_year_total_internal_gain']),
            'resid_heating_price': float(self.config['RES_base_year_heating_price']),
            'resid_cooling_price': float(self.config['RES_base_year_cooling_price']),
            'comm_heating_price': float(self.config['NRES_base_year_heating_price']),
            'comm_cooling_price': float(self.config['NRES_base_year_cooling_price'])
        }

    def get_year_data(self, data):
        """
        Read in data for a given year
        """
        # Read spatial datasets
        temperature = self.read_spatial_data('temperature_data', data)
        resid_building_area = self.read_spatial_data('RES_building_area_data', data, mask=self.resid_coverage_percent_mask)
        comm_building_area = self.read_spatial_data('NRES_building_area_data', data, mask=self.comm_coverage_percent_mask)
        building_height = self.read_spatial_data('building_height_data', data)
        income_per_capita = self.read_spatial_data('income_per_capita', data)
        income_per_capita = income_per_capita['income']

        # Align spatial datasets
        temperature, \
        resid_building_area, \
        comm_building_area, \
        building_height, \
        income_per_capita = xr.align(temperature, 
                                     resid_building_area, 
                                     comm_building_area,
                                     building_height, 
                                     income_per_capita,
                                     join='override')

        # Surface to floor ratio
        resid_surface_to_floor_area_ratio, resid_floor_space, resid_total_floor_space, resid_building_area, resid_building_height = self.get_surface_to_floor_area_ratio(resid_building_area, building_height)
        comm_surface_to_floor_area_ratio, comm_floor_space, comm_total_floor_space, comm_building_area, comm_building_height = self.get_surface_to_floor_area_ratio(comm_building_area, building_height)

        # Return data in dictionary including constants
        return {
            'temperature': temperature,
            'resid_area': resid_building_area,
            'comm_area': comm_building_area,
            'resid_height': resid_building_height,
            'comm_height': comm_building_height,
            'income': income_per_capita,
            'resid_surface_to_floor_area_ratio': resid_surface_to_floor_area_ratio,
            'comm_surface_to_floor_area_ratio': comm_surface_to_floor_area_ratio,
            'resid_floor_space': resid_floor_space,
            'comm_floor_space': comm_floor_space,
            'resid_total_floor_space': resid_total_floor_space,
            'comm_total_floor_space': comm_total_floor_space,
            'year': int(data['year']),
            'resid_total_internal_gain': float(data['RES_total_internal_gain']),
            'comm_total_internal_gain': float(data['NRES_total_internal_gain']),
            'resid_heating_price': float(data['RES_heating_price']),
            'resid_cooling_price': float(data['RES_cooling_price']),
            'comm_heating_price': float(data['NRES_heating_price']),
            'comm_cooling_price': float(data['NRES_cooling_price'])
        }

    def get_surface_to_floor_area_ratio(self, building_area, building_height):
        """
        Calculate surface to floor area ratio using building area and building height
        """
        logging.info('Calculating surface area to floor space ratio')

        # Formatting
        building_area = building_area['band_data'].squeeze('band').drop_vars(['band', 'spatial_ref']).transpose('y', 'x')
        building_height = building_height['band_data'].squeeze('band').drop_vars(['band', 'spatial_ref']).transpose('y', 'x')

        # Floor space
        floor_space = building_area * building_height / 3
        total_floor_space = np.nansum(floor_space.data)

        # Length and Width assuming square building
        lw = np.sqrt(building_area)

        # Surface area, 4 sides + roof
        surface_area = (4 * (lw * building_height)) + (lw * lw)

        # Surface to floor area ratio
        s2far = surface_area / floor_space

        return s2far, floor_space, total_floor_space, building_area, building_height

    def read_spatial_data(self, key, data, mask=None):
        """
        Read in spatial datasets using Xarray

        :param key:         Key of in config file for path to data to read
        :type key:          string
        :return:            Xarray DataSet
        """

        logging.info(f'Reading {key} data')

        # Assume datasets are in same folder as config_file
        if os.path.exists(os.path.abspath(os.path.join(self.dir_root, data[key]))):
            spatial_data = xr.open_mfdataset(os.path.abspath(os.path.join(self.dir_root, data[key])))
        else: # If user gives full path
            spatial_data = xr.open_mfdataset(os.path.abspath(data[key]))

        # if mask is None:
        #     return spatial_data.compute()
        
        # _, spatial_data = xr.align(mask, spatial_data, join='override')
        
        return spatial_data.compute() #.where(~mask.isnull()).compute()
