"""
@Date:
@authors:
@Project: bed v0.0

License:  BSD 2-Clause, see LICENSE and DISCLAIMER files
Copyright (c) 2022, Battelle Memorial Institute

"""

import os

from numpy import log, exp, isnan, nansum, power
from xarray import align, Dataset

from bed.read_config import read_config
from bed.read_data import Data
from bed.diagnostics import diagnostics
from bed.demand import *


class Bed:
    """ Model wrapper for bed"""

    def __init__(self, config_file='', run_diagnostics=True):

        # Read data
        self.data = Data(config_file)

        # Shared data extraction
        temperature_variable_name = self.data.data_dict['base_year']['temperature_variable_name']
        temperature_units = self.data.data_dict['base_year']['temperature_units']
        comfortable_temperature_lower = self.data.data_dict['base_year']['comfortable_temperature_lower']
        comfortable_temperature_upper = self.data.data_dict['base_year']['comfortable_temperature_upper']

        # Calculate degree hours
        for key, data in self.data.data_dict.items():
            self.data.data_dict[key]['degree_hours'] = self.temperature_to_degree_hours(
                temperature=data['temperature'][temperature_variable_name],
                temperature_unit=temperature_units,
                comfortable_temperature_lower=comfortable_temperature_lower,
                comfortable_temperature_upper=comfortable_temperature_upper
            )

        # Do Calibration
        calibration_coefficients = self.calibration()

        # Calculate building energy demand for each input
        self.energy_demand = {}
        for key, data in self.data.data_dict.items():
            # Skip calibration year
            if key == 'base_year':
                next
            else:
                self.energy_demand[key] = self.get_demand(data, self.data.data_dict['base_year'], calibration_coefficients)
            ...

        # Save Data Out
        save_data(self.energy_demand, self.data.dir_outputs)

        # diagnostics
        if run_diagnostics:
            diagnostics(self.data.data_dict, self.energy_demand, self.data.dir_diagnostics, calibration_coefficients)
        ...

    def temperature_to_degree_hours(
        self,
        temperature, 
        temperature_unit='F', 
        comfortable_temperature_lower=65,
        comfortable_temperature_upper=70
        ):
        """
        Calculating heating and cooling degree hours (days?)
        :param temperature_unit:                    String for temperature unit
        :param comfortable_temperature:             Array for comfortable temperature
        :param weighted_population:                 Array for weighted population (unitless)
        :return:                                    Dict of Float Xarrays for HDD and CDD
        """
        logging.info('Starting function temperature_to_degree_hours.')

        # TODO: Convert temperature to °C?

        # For HDD
        # Get difference in temp and threshold, and flip so that colder values are positive
        hdd_data = -1 * (temperature - comfortable_temperature_lower)
        # Keep only values above axis
        hdd_data = hdd_data.where(hdd_data > 0, 0)
        # Integrate using trapezoidal method
        hdd_data = hdd_data.integrate('time', datetime_unit='h')
        # Integration puts 0 in place of nan, so reinstate the mask from temp data
        hdd_data = hdd_data.where(~isnan(temperature.isel(time=0))).drop_vars('time')

        # For HDD
        # Get difference in temp and threshold
        cdd_data = (temperature - comfortable_temperature_upper)
        # Keep only values above axis
        cdd_data = cdd_data.where(cdd_data > 0, 0)
        # Integrate using trapezoidal method
        cdd_data = cdd_data.integrate('time', datetime_unit='h')
        # Integration puts 0 in place of nan, so reinstate the mask from temp data
        cdd_data = cdd_data.where(~isnan(temperature.isel(time=0))).drop_vars('time')

        # Total number of hours per grid cell in a year beyond threshold
        degree_hours = {
            'hdd': hdd_data.transpose('y', 'x'),
            'cdd': cdd_data.transpose('y', 'x')
        }

        logging.info('Function temperature_to_degree_hours completed.')

        return degree_hours

    def get_demand(self, year_data, base_year_data, calibration_coefficients):
        """
        :param year_data:                           Dict holds data for the current year to estimate demand
        :param base_year_data:                      Dict holds data for the calibration year
        :param calibration_coefficients:            Dict of dict of Arrays that hold calibration values for res and comm sectors for heating and cooling
        :return:                                    Dict of demand data
        """

        logging.info('Starting function demand.')

        demand_results = {
            'resid': resid_demand(year_data, base_year_data, calibration_coefficients['resid']), 
            'comm': comm_demand(year_data, base_year_data, calibration_coefficients['comm'])
        }

        logging.info('Function demand completed.')

        return demand_results

    def calibration(self):
        """
        Find the heating and cooling calibration coefficients in the model for each sector in each grid cell
        """

        # Base year data
        data = self.data.data_dict['base_year']

        return {
            'resid': resid_calibration(data),
            'comm': comm_calibration(data)
        }
    

def k_calibration(technical_component, demand, satiation_factor):
    """
    Calibrating unit-less k term
    :param usa_base_year_demand:             Float demand in USA for given year
    :param usa_degree_hours:                 Float HDD/CDD in USA for given year
    :param base_year_demand:                 Float for thermal conductance (GJ/m2 hour C)
    :param technical_component               Float array term inside first parentheses Eq (3) and (4)
    :return:                                 Float array of calibration coefficients
    """
    # Satiation level assumed to be max of observed base-year demand, and satiation level in USA modified using ratio of degree hours
    satiation_level = demand * satiation_factor 

    # Solve for k
    k = satiation_level / technical_component

    return k


def mu_calibration(demand, technical_component, calibration_coefficient, prices, income_per_capita):
    """
    Calibrating unit-less mu term
    :param base_year_demand:                 Float for thermal conductance (GJ/m2 hour C)
    :param technical_component               Float array term inside first parentheses Eq (3) and (4)
    :param calibration_coefficient           Float array of the calibration coefficient "k"
    :param prices                            Float avg service prices
    :param income_per_capita                 Float income per capita
    :return:                                 Float array of calibration coefficients "mu"
    """
    # Breaking up mu calculation into multiple terms
    term_one = calibration_coefficient * technical_component
    term_two = prices * log(1-demand/term_one)
    mu = -log(2) * income_per_capita / term_two

    return mu


def resid_calibration(data):
    """
    Do calibration for residential sector
    """
    # Convert total internal gain to internal gain per unit floor-space
    internal_gain = data['resid_total_internal_gain'] / data['resid_total_floor_space']

    # Convert total demand to demand per unit floor-space
    fs_times_hdd = data['resid_floor_space'] * data['degree_hours']['hdd']
    fs_times_cdd = data['resid_floor_space'] * data['degree_hours']['cdd']
    # TODO: Normalize bracketed term ?
    heating_demand = data['resid_heating_demand'] * (fs_times_hdd / nansum(fs_times_hdd.data) / data['resid_floor_space'])
    cooling_demand = data['resid_cooling_demand'] * (fs_times_cdd / nansum(fs_times_cdd.data) / data['resid_floor_space'])

    # Getting U-factor given improvement rate and target year
    years_bt_u_factor_target_year = data['year'] - data['u_factor_target_year']
    u_factor_improvement = power(1-data['u_factor_improvement_rate'], years_bt_u_factor_target_year)

    # Calculate first parentheses term
    technical_component_h = data['degree_hours']['hdd'] * data['resid_u_factor'] * u_factor_improvement * data['resid_surface_to_floor_area_ratio'] - internal_gain
    technical_component_c = data['degree_hours']['cdd'] * data['resid_u_factor'] * u_factor_improvement * data['resid_surface_to_floor_area_ratio'] + internal_gain

    # K calibration
    k_h = k_calibration(technical_component_h, heating_demand, data['satiation_factor'])
    k_c = k_calibration(technical_component_c, cooling_demand, data['satiation_factor'])

    # Mu calibration
    mu_h = mu_calibration(demand=heating_demand,
                            technical_component=technical_component_h,
                            calibration_coefficient=k_h,
                            prices=data['resid_heating_price'],
                            income_per_capita=data['income'])
    mu_c = mu_calibration(demand=cooling_demand,
                            technical_component=technical_component_c,
                            calibration_coefficient=k_c,
                            prices=data['resid_cooling_price'],
                            income_per_capita=data['income'])
    
    return {
        'k_h': k_h,
        'k_c': k_c,
        'mu_h': mu_h,
        'mu_c': mu_c
    }


def comm_calibration(data):
    """
    Do calibration for non-residential sector
    """
    # Convert total internal gain to internal gain per unit floor-space
    internal_gain = data['comm_total_internal_gain'] / data['comm_total_floor_space']

    # Convert total demand to demand per unit floor-space
    fs_times_hdd = data['comm_floor_space'] * data['degree_hours']['hdd']
    fs_times_cdd = data['comm_floor_space'] * data['degree_hours']['cdd']
    # TODO: Normalize bracketed term ?
    heating_demand = data['comm_heating_demand'] * (fs_times_hdd / nansum(fs_times_hdd.data) / data['comm_floor_space'])
    cooling_demand = data['comm_cooling_demand'] * (fs_times_cdd / nansum(fs_times_cdd.data) / data['comm_floor_space'])

    # Getting U-factor given improvement rate and target year
    years_bt_u_factor_target_year = data['year'] - data['u_factor_target_year']
    u_factor_improvement = power(1-data['u_factor_improvement_rate'], years_bt_u_factor_target_year)

    # Calculate first parentheses term
    technical_component_h = data['degree_hours']['hdd'] * data['comm_u_factor'] * u_factor_improvement * data['comm_surface_to_floor_area_ratio'] - internal_gain
    technical_component_c = data['degree_hours']['cdd'] * data['comm_u_factor'] * u_factor_improvement * data['comm_surface_to_floor_area_ratio'] + internal_gain

    # K calibration
    k_h = k_calibration(technical_component_h, heating_demand, data['satiation_factor'])
    k_c = k_calibration(technical_component_c, cooling_demand, data['satiation_factor'])

    # Mu calibration
    mu_h = mu_calibration(demand=heating_demand,
                            technical_component=technical_component_h,
                            calibration_coefficient=k_h,
                            prices=data['comm_heating_price'],
                            income_per_capita=data['income'])
    mu_c = mu_calibration(demand=cooling_demand,
                            technical_component=technical_component_c,
                            calibration_coefficient=k_c,
                            prices=data['comm_cooling_price'],
                            income_per_capita=data['income'])
    
    return {
        'k_h': k_h,
        'k_c': k_c,
        'mu_h': mu_h,
        'mu_c': mu_c
    }


def resid_demand(year_data, base_year_data, calibration_coefficients):
    """
    Calculating the estimated building heating and cooling energy demand for the residential sector
    """
    logging.info('Starting residential demand.')

    # Getting U-factor given improvement rate and target year
    years_bt_u_factor_target_year = year_data['year'] - base_year_data['u_factor_target_year']
    u_factor_improvement = power(1-base_year_data['u_factor_improvement_rate'], years_bt_u_factor_target_year)

    # Convert total internal gain to internal gain per unit floor-space
    internal_gain = year_data['resid_total_internal_gain'] / year_data['resid_total_floor_space']

    # Evaluating component of demand equation
    technical_component_h = year_data['degree_hours']['hdd'] * base_year_data['resid_u_factor'] * u_factor_improvement * year_data['resid_surface_to_floor_area_ratio'] - internal_gain
    technical_component_c = year_data['degree_hours']['cdd'] * base_year_data['resid_u_factor'] * u_factor_improvement * year_data['resid_surface_to_floor_area_ratio'] + internal_gain

    # Calculate gridded demand
    economic_component_h = 1 - exp(- (log(2) * year_data['income']) / (calibration_coefficients['mu_h'] * year_data['resid_heating_price']) )
    economic_component_c = 1 - exp(- (log(2) * year_data['income']) / (calibration_coefficients['mu_c'] * year_data['resid_cooling_price']) )
    demand_h = calibration_coefficients['k_h'] * technical_component_h * economic_component_h
    demand_c = calibration_coefficients['k_c'] * technical_component_c * economic_component_c

    logging.info('Function demand completed.')

    return {
        'demand_h': demand_h.fillna(0).where(~isnan(year_data['degree_hours']['hdd'])), 
        'demand_c': demand_c.fillna(0).where(~isnan(year_data['degree_hours']['hdd']))
    }


def comm_demand(year_data, base_year_data, calibration_coefficients):
    """
    Calculating the estimated building heating and cooling energy demand for the non-residential sectors
    """
    logging.info('Starting non-residential demand.')

    # Getting U-factor given improvement rate and target year
    years_bt_u_factor_target_year = year_data['year'] - base_year_data['u_factor_target_year']
    u_factor_improvement = power(1-base_year_data['u_factor_improvement_rate'], years_bt_u_factor_target_year)

    # Convert total internal gain to internal gain per unit floor-space
    internal_gain = year_data['comm_total_internal_gain'] / year_data['comm_total_floor_space']

    # Evaluating component of demand equation
    technical_component_h = year_data['degree_hours']['hdd'] * base_year_data['comm_u_factor'] * u_factor_improvement * year_data['comm_surface_to_floor_area_ratio'] - internal_gain
    technical_component_c = year_data['degree_hours']['cdd'] * base_year_data['comm_u_factor'] * u_factor_improvement * year_data['comm_surface_to_floor_area_ratio'] + internal_gain

    # Calculate gridded demand
    economic_component_h = 1 - exp(- (log(2) * year_data['income']) / (calibration_coefficients['mu_h'] * year_data['comm_heating_price']) )
    economic_component_c = 1 - exp(- (log(2) * year_data['income']) / (calibration_coefficients['mu_c'] * year_data['comm_cooling_price']) )
    demand_h = calibration_coefficients['k_h'] * technical_component_h * economic_component_h
    demand_c = calibration_coefficients['k_c'] * technical_component_c * economic_component_c

    logging.info('Function demand completed.')

    return {
        'demand_h': demand_h.fillna(0).where(~isnan(year_data['degree_hours']['hdd'])), 
        'demand_c': demand_c.fillna(0).where(~isnan(year_data['degree_hours']['hdd']))
    }


def save_data(energy_demand, output_dir):
    """
    Save the final energy demand data
    """

    logging.info('Writing Output')

    encoding={
        'zlib': True,
        'shuffle': True,
        'complevel': 5,
        'fletcher32': False,
        'contiguous': False,
        'dtype': 'float32',
        'missing_value': 1.00E+20,
        '_FillValue': 1.00E+20
    }
    final_encoding = {
        'residential_heating': encoding,
        'residential_cooling': encoding,
        'non-residential_heating': encoding,
        'non-residential_cooling': encoding
    }
    for key, data in energy_demand.items():
        final_output = Dataset({
            'residential_heating': data['resid']['demand_h'],
            'residential_cooling': data['resid']['demand_c'],
            'non-residential_heating': data['comm']['demand_h'],
            'non-residential_cooling': data['comm']['demand_c']
        })
        final_output.to_netcdf(os.path.join(output_dir, f'building_energy_demand_{key}.nc'), encoding=final_encoding)
        ...
    ...
