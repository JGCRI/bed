"""
@Date:
@authors:
@Project: bed v0.0

License:  BSD 2-Clause, see LICENSE and DISCLAIMER files
Copyright (c) 2022, Battelle Memorial Institute

"""

from numpy import log, exp, isnan, nansum
from xarray import align

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

        # diagnostics
        if run_diagnostics:
            diagnostics(self.data.data_dict, self.energy_demand, self.data.dir_diagnostics)

        # TODO: Save Data Out
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
        :param degree_hours:                        Array for degree hours (Hours)
        :param thermal_conductance:                 Float for thermal conductance (GJ/m2 hour C)
        :param surface_to_floor_ratio:              Float for surface to floor ratio (Unitless)
        :param internal_gain:                       Float for Internal Gain (GJ/m2)
        :param income_per_capita:                   Array for per-capita income (2010 USD)
        :param service_price:                       Dict of Arrays for weighted average of technologies used for heating "H" and cooling "C" (2010 USD)
        :return:                                    Array for demand
        """

        logging.info('Starting function demand.')

        # TODO: Calculate actual U-Factor for given year using improvement rate

        # Convert total internal gain to internal gain per unit floor-space
        internal_gain = year_data['total_internal_gain'] / year_data['total_floor_space']

        # Evaluating component of demand equation
        technical_component_h = year_data['degree_hours']['hdd'] * base_year_data['resid_u_factor'] * year_data['surface_to_floor_area_ratio'] - internal_gain
        technical_component_c = year_data['degree_hours']['cdd'] * base_year_data['resid_u_factor'] * year_data['surface_to_floor_area_ratio'] + internal_gain

        # Calculate gridded demand
        economic_component_h = 1 - exp(- (log(2) * year_data['income']) / (calibration_coefficients['mu_h'] * year_data['heating_price']) )
        economic_component_c = 1 - exp(- (log(2) * year_data['income']) / (calibration_coefficients['mu_c'] * year_data['cooling_price']) )
        demand_h = calibration_coefficients['k_h'] * technical_component_h * economic_component_h
        demand_c = calibration_coefficients['k_c'] * technical_component_c * economic_component_c

        logging.info('Function demand completed.')

        return {
            'demand_h': demand_h.fillna(0).where(~isnan(year_data['degree_hours']['hdd'])), 
            'demand_c': demand_c.fillna(0).where(~isnan(year_data['degree_hours']['hdd']))
            }

    def calibration(self):

        # Base year data
        data = self.data.data_dict['base_year']

        # Convert total internal gain to internal gain per unit floor-space
        internal_gain = data['total_internal_gain'] / data['total_floor_space']

        # Convert total demand to demand per unit floor-space
        fs_times_hdd = data['floor_space'] * data['degree_hours']['hdd']
        fs_times_cdd = data['floor_space'] * data['degree_hours']['cdd']
        # TODO: Normalize bracketed term ?
        heating_demand = data['heating_demand'] * (fs_times_hdd / nansum(fs_times_hdd.data) / data['floor_space'])
        cooling_demand = data['cooling_demand'] * (fs_times_cdd / nansum(fs_times_cdd.data) / data['floor_space'])

        # Evaluating component of demand equation
        # TODO: Split up by commercial and residential
        # TODO: Calculate actual U-Factor for given year using improvement rate
        technical_component_h = data['degree_hours']['hdd'] * data['resid_u_factor'] * data['surface_to_floor_area_ratio'] - internal_gain
        technical_component_c = data['degree_hours']['cdd'] * data['resid_u_factor'] * data['surface_to_floor_area_ratio'] + internal_gain

        # K calibration
        k_h = self.k_calibration(technical_component_h, heating_demand, data['satiation_factor'])
        k_c = self.k_calibration(technical_component_c, cooling_demand, data['satiation_factor'])

        # Mu calibration
        mu_h = self.mu_calibration(demand=heating_demand,
                                   technical_component=technical_component_h,
                                   calibration_coefficient=k_h,
                                   prices=data['heating_price'],
                                   income_per_capita=data['income'])
        mu_c = self.mu_calibration(demand=cooling_demand,
                                   technical_component=technical_component_c,
                                   calibration_coefficient=k_c,
                                   prices=data['cooling_price'],
                                   income_per_capita=data['income'])
        
        return {
            'k_h': k_h,
            'k_c': k_c,
            'mu_h': mu_h,
            'mu_c': mu_c
        }
    
    def k_calibration(self, technical_component, demand, satiation_factor):
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

    def mu_calibration(self, 
                       demand,
                       technical_component,
                       calibration_coefficient, 
                       prices, 
                       income_per_capita):
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
    