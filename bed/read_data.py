import logging
import pandas as pd

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
            self.example_data_set = pd.read_csv(config['path_example_data_set'])