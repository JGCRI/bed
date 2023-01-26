"""
@Date:
@authors:
@Project: bed v0.0

License:  BSD 2-Clause, see LICENSE and DISCLAIMER files
Copyright (c) 2022, Battelle Memorial Institute

"""

from bed.read_config import read_config

class Bed:
    """ Model wrapper for bed"""

    def __init__(self, config_file='config'):
        self.var1 = 0.125
        self.var = 5

        self.config = read_config(config_file)

        # read data
        # self.d = read_data()

        # calculate building energy demand (tas)
            # heating and cooling degree hours

            # heating energy demand

            # cooling energy demand

        # diagnostics

        # write outputs

        # clean up and close
