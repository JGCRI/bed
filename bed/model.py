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

        # Read spatial data + config
        # Data object contains:
        #   - Temperature
        #   - Surface to Floor space ratio
        self.data = Data(config_file)

        # User defined base year demand
        self.base_year_heating_demand = float(self.data.config['base_year_heating_demand'])
        self.base_year_cooling_demand = float(self.data.config['base_year_cooling_demand'])
        self.base_year_satiation_factor = float(self.data.config['base_year_satiation_factor'])

        # Service Prices
        self.base_year_service_prices = {
            'H': self.data.config['base_year_heating_price'],
            'C': self.data.config['base_year_cooling_price']
        }
        self.service_prices = {
            'H': self.data.config['heating_price'],
            'C': self.data.config['cooling_price']
        }

        # Internal gain
        self.total_internal_gain = float(self.data.config['total_internal_gain'])
        self.base_year_total_internal_gain = float(self.data.config['base_year_total_internal_gain'])

        # Thermal Conductance / U-Factor improvement rate
        self.thermal_conductance = self.data.config['thermal_conductance']
        self.base_year_thermal_conductance = self.data.config['base_year_thermal_conductance']

        # Calculate degree hours
        self.degree_hours = self.temperature_to_degree_hours(
            self.data.temperature[self.data.config['temperature_variable_name']], 
            temperature_unit=self.data.config['temperature_units'],
            comfortable_temperature=self.data.config['comfortable_temperature']
            )
        self.base_year_degree_hours = self.temperature_to_degree_hours(
            self.data.base_year_temperature[self.data.config['temperature_variable_name']],
            temperature_unit=self.data.config['temperature_units'],
            comfortable_temperature=self.data.config['comfortable_temperature']
            )

        # Calculate building energy demand
        self.demand = self.get_demand(income_per_capita=1)

        # diagnostics
        if run_diagnostics:
            diagnostics(self.data, self.degree_hours, self.demand, {
                'area': self.data.building_area,
                'height': self.data.building_height,
                'floor': self.data.floor_space,
                's2far': self.data.surface_to_floor_area_ratio
            })
        ...

    def temperature_to_degree_hours(self, temperature, temperature_unit='F', comfortable_temperature=65):
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
        hdd_data = -1 * (temperature - comfortable_temperature)
        # Keep only values above axis
        hdd_data = hdd_data.where(hdd_data > 0, 0)
        # Integrate using trapezoidal method
        hdd_data = hdd_data.integrate('time', datetime_unit='h')
        # Integration puts 0 in place of nan, so reinstate the mask from temp data
        hdd_data = hdd_data.where(~isnan(temperature.isel(time=0))).drop_vars('time')

        # For HDD
        # Get difference in temp and threshold
        cdd_data = (temperature - comfortable_temperature)
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

    def get_demand(self,  
                   income_per_capita=1):
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

        # Convert total internal gain to internal gain per unit floor-space
        internal_gain = self.total_internal_gain / self.data.total_floor_space
        base_year_internal_gain = self.base_year_total_internal_gain / self.data.base_year_total_floor_space

        # Convert total demand to demand per unit floor-space
        # Align, removes floating point errors of lat/lon alignment
        self.data.floor_space, self.base_year_degree_hours['hdd'], self.base_year_degree_hours['cdd'] = align(self.data.floor_space, self.base_year_degree_hours['hdd'], self.base_year_degree_hours['cdd'], join='override')
        fs_times_hdd = self.data.floor_space * self.base_year_degree_hours['hdd']
        fs_times_cdd = self.data.floor_space * self.base_year_degree_hours['cdd']
        self.base_year_heating_demand = self.base_year_heating_demand * fs_times_hdd / nansum(fs_times_hdd.data)
        self.base_year_cooling_demand = self.base_year_cooling_demand * fs_times_cdd / nansum(fs_times_cdd.data)

        # Evaluating component of demand equation
        self.degree_hours['hdd'], self.degree_hours['cdd'], self.data.surface_to_floor_area_ratio = align(self.degree_hours['hdd'], self.degree_hours['cdd'], self.data.surface_to_floor_area_ratio, join = 'override')
        self.base_year_degree_hours['hdd'], self.base_year_degree_hours['cdd'], self.data.base_year_surface_to_floor_area_ratio = align(self.degree_hours['hdd'], self.degree_hours['cdd'], self.data.surface_to_floor_area_ratio, join = 'override')
        technical_component_h = self.degree_hours['hdd'] * self.thermal_conductance * self.data.surface_to_floor_area_ratio - internal_gain
        technical_component_c = self.degree_hours['cdd'] * self.thermal_conductance * self.data.surface_to_floor_area_ratio + internal_gain
        base_year_technical_component_h = self.base_year_degree_hours['hdd'] * self.base_year_thermal_conductance * self.data.base_year_surface_to_floor_area_ratio - base_year_internal_gain
        base_year_technical_component_c = self.base_year_degree_hours['cdd'] * self.base_year_thermal_conductance * self.data.base_year_surface_to_floor_area_ratio + base_year_internal_gain

        # Calibrate k:
        #       Set income to infinity, and let dh/dc now represent level of satiated demand -
        #       (this is where they use USA as a benchmark and calc other regions from Eqs S1 and S2)
        k_h = self.k_calibration(base_year_technical_component_h, self.base_year_heating_demand)
        k_c = self.k_calibration(base_year_technical_component_c, self.base_year_cooling_demand)

        # Calibrate mu:
        #       Need base year demand so that we can solve for mu
        mu_h = self.mu_calibration(demand=self.base_year_heating_demand,
                                   technical_component=technical_component_h,
                                   calibration_coefficient=k_h,
                                   prices=self.base_year_service_prices['H'],
                                   income_per_capita=self.data.base_year_income_per_capita)
        mu_c = self.mu_calibration(demand=self.base_year_cooling_demand,
                                   technical_component=technical_component_c,
                                   calibration_coefficient=k_c,
                                   prices=self.base_year_service_prices['C'],
                                   income_per_capita=self.data.base_year_income_per_capita)

        # Calculate gridded demand
        economic_component_h = 1 - exp(- (log(2) * self.data.income_per_capita) / (mu_h * self.service_prices['H']) )
        economic_component_c = 1 - exp(- (log(2) * self.data.income_per_capita) / (mu_c * self.service_prices['C']) )
        print(f'size of economic_component_h: {economic_component_h.sizes}\nsize of k_h: {k_h.sizes}\nsize of technical_component_h: {technical_component_h.sizes}')
        k_h, technical_component_h, economic_component_h, self.degree_hours['hdd'] = align(k_h, technical_component_h, economic_component_h, self.degree_hours['hdd'], join = 'override')
        k_c, technical_component_c, economic_component_c, self.degree_hours['cdd'] = align(k_c, technical_component_c, economic_component_c, self.degree_hours['cdd'], join = 'override')
        demand_h = k_h * technical_component_h * economic_component_h
        demand_c = k_c * technical_component_c * economic_component_c

        logging.info('Function demand completed.')

        return {
            'demand_h': demand_h.fillna(0).where(~isnan(self.degree_hours['hdd'])), 
            'demand_c': demand_c.fillna(0).where(~isnan(self.degree_hours['hdd']))
            }

    def k_calibration(self, technical_component, demand):
        """
        Calibrating unit-less k term
        :param usa_base_year_demand:             Float demand in USA for given year
        :param usa_degree_hours:                 Float HDD/CDD in USA for given year
        :param base_year_demand:                 Float for thermal conductance (GJ/m2 hour C)
        :param technical_component               Float array term inside first parentheses Eq (3) and (4)
        :return:                                 Float array of calibration coefficients
        """
        # Satiation level assumed to be max of observed base-year demand, and satiation level in USA modified using ratio of degree hours
        satiation_level = demand * self.base_year_satiation_factor 

        # Solve for k
        satiation_level, technical_component = align(satiation_level, technical_component, join = 'override')
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
        demand, technical_component, calibration_coefficient = align(demand, technical_component, calibration_coefficient, join = 'override')
        term_one = calibration_coefficient * technical_component
        term_two = prices * log(1-demand/term_one)
        mu = -log(2) * income_per_capita / term_two

        return mu
    