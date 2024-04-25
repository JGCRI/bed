"""
@Date:
@authors:
@Project: bed v0.0

License:  BSD 2-Clause, see LICENSE and DISCLAIMER files
Copyright (c) 2022, Battelle Memorial Institute

"""

from numpy import maximum, log, exp, isnan
from bed.read_config import read_config
from bed.read_data import Data
from bed.diagnostics import diagnostics
from bed.demand import *


class Bed:
    """ Model wrapper for bed"""

    def __init__(self, config_file='', run_diagnostics=True):

        # Read data
        # Data object contains:
        #   - Temperature
        #   - Surface to Floor space ratio
        self.data = Data(config_file)

        # Calculate degree hours
        self.degree_hours = self.temperature_to_degree_hours(temperature_unit='K', 
                                                             comfortable_temperature=291.483)

        # Calculate building energy demand
        self.demand_heat = self.demand(thermal_conductance=1,
                                       surface_to_floor_ratio=self.data.surface_to_floor_area_ratio, 
                                       internal_gain=1, 
                                       income_per_capita=1, 
                                       service_price={'H': 1, 'C': 1})

        # diagnostics
        if run_diagnostics:
            diagnostics(self.data)
        ...

    def temperature_to_degree_hours(self, temperature_unit='F', comfortable_temperature=65):
        """
        Calculating heating and cooling degree hours (days?)
        :param temperature_unit:                    String for temperature unit
        :param comfortable_temperature:             Array for comfortable temperature
        :param weighted_population:                 Array for weighted population (unitless)
        :return:                                    Dict of Float Xarrays for HDD and CDD
        """
        logging.info('Starting function temperature_to_degree_hours.')

        # For HDD
        # Get difference in temp and threshold, and flip so that colder values are positive
        hdd_data = -1 * (self.data.temperature - comfortable_temperature)
        # Keep only values above axis
        hdd_data = hdd_data.where(hdd_data > 0, 0)
        # Integrate using trapezoidal method
        hdd_data = hdd_data.integrate('time', datetime_unit='h')
        # Integration puts 0 in place of nan, so reinstate the mask from temp data
        hdd_data = hdd_data.where(~isnan(self.data.temperature.isel(time=0)))

        # For HDD
        # Get difference in temp and threshold
        cdd_data = (self.data.temperature - comfortable_temperature)
        # Keep only values above axis
        cdd_data = cdd_data.where(cdd_data > 0, 0)
        # Integrate using trapezoidal method
        cdd_data = cdd_data.integrate('time', datetime_unit='h')
        # Integration puts 0 in place of nan, so reinstate the mask from temp data
        cdd_data = cdd_data.where(~isnan(self.data.temperature.isel(time=0)))

        # Total number of hours per grid cell in a year beyond threshold
        degree_hours = {
            'hdd': hdd_data,
            'cdd': cdd_data
        }

        logging.info('Function temperature_to_degree_hours completed.')

        return degree_hours

    def demand(self, 
               thermal_conductance=1, 
               surface_to_floor_ratio=1, 
               internal_gain=1, 
               income_per_capita=1, 
               service_price={'H': 1, 'C': 1}):
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

        technical_component_h = self.degree_hours['hdd'] * thermal_conductance * surface_to_floor_ratio - internal_gain
        technical_component_c = self.degree_hours['cdd'] * thermal_conductance * surface_to_floor_ratio + internal_gain

        # Calibrate k:
        #       Set income to infinity, and let dh/dc now represent level of satiated demand -
        #       (this is where they use USA as a benchmark and calc other regions from Eqs S1 and S2)
        k_h = self.k_calibration(usa_base_year_demand=1, 
                                 usa_degree_hours=1, 
                                 base_year_demand=1, 
                                 technical_component=technical_component_h,
                                 degree_type='hdd')
        k_c = self.k_calibration(usa_base_year_demand=1, 
                                 usa_degree_hours=1, 
                                 base_year_demand=1, 
                                 technical_component=technical_component_c,
                                 degree_type='cdd')

        # Calibrate mu:
        #       Need base year demand so that we can solve for mu
        mu_h = self.mu_calibration(base_year_demand=1,
                                   technical_component=technical_component_h,
                                   calibration_coefficient=k_h,
                                   prices=service_price['H'],
                                   income_per_capita=income_per_capita)
        mu_c = self.mu_calibration(base_year_demand=1,
                                   technical_component=technical_component_c,
                                   calibration_coefficient=k_c,
                                   prices=service_price['C'],
                                   income_per_capita=income_per_capita)

        # Calculate gridded demand
        economic_component_h = 1 - exp(- (log(2) * income_per_capita) / (mu_h * service_price['H']) )
        economic_component_c = 1 - exp(- (log(2) * income_per_capita) / (mu_c * service_price['C']) )
        demand_h = k_h * technical_component_h * economic_component_h
        demand_c = k_c * technical_component_c * economic_component_c

        logging.info('Function demand completed.')

        return {'demand_h': demand_h, 'demand_c': demand_c}

    def k_calibration(self, usa_base_year_demand, usa_degree_hours, base_year_demand, technical_component, degree_type='hdd'):
        """
        Calibrating unit-less k term
        :param usa_base_year_demand:             Float demand in USA for given year
        :param usa_degree_hours:                 Float HDD/CDD in USA for given year
        :param base_year_demand:                 Float for thermal conductance (GJ/m2 hour C)
        :param technical_component               Float array term inside first parentheses Eq (3) and (4)
        :return:                                 Float array of calibration coefficients
        """
        # Satiation level assumed to be max of observed base-year demand, and satiation level in USA modified using ratio of degree hours
        satiation_level = (self.degree_hours[degree_type] / usa_degree_hours) * usa_base_year_demand * 1.1
        satiation_level = maximum(satiation_level, base_year_demand)

        # Solve for k
        k = satiation_level / technical_component

        return k

    def mu_calibration(self, 
                       base_year_demand, 
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
        term_two = prices * log(1-base_year_demand/term_one)
        mu = -log(2) * income_per_capita / term_two

        return mu
    