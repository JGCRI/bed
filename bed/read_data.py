import logging
import pandas as pd
import xarray as xr
import os as os

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

    def __init__(self, config=''):
        """
        :param config:         configuration file path
        :type config:          yaml
        :return:               Data
        """

        logging.info('Starting function read_config...')

        self.config = config

        if config != '':

            # Create folders
            self.dir_root = os.path.abspath(self.config['dir_root'])
            self.dir_outputs = os.path.abspath(os.path.join(self.dir_root, self.config['dir_outputs']))
            self.dir_diagnostics = os.path.abspath(os.path.join(self.dir_outputs, "diagnostics"))

            # Create folders if they don't exist
            self.example_dataset = pd.read_csv(self.config['path_example_data_set'])
            self.temperature = xr.open_dataset(self.config['path_temperature_ncdf'])

