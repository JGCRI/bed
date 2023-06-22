"""
@Date:
@authors:
@Project: bed v0.0

License:  BSD 2-Clause, see LICENSE and DISCLAIMER files
Copyright (c) 2022, Battelle Memorial Institute

"""

from bed.read_config import read_config
from bed.read_data import Data
from bed.diagnostics import diagnostics
from bed.demand import *


class Bed:
    """ Model wrapper for bed"""

    def __init__(self, config_file='', run_diagnostics=True):

        # Read in Config File
        self.config = read_config(config_file)

        # Read data
        self.data = Data(self.config)

        # Calculate degree hours
        self.degree_hours = temperature_to_degree_hours(temperature=1, weighted_population=1,
                                                        temperature_unit='F', comfortable_temperature=65)

        # Calculate building energy demand
        self.demand_heat = demand(calibration_coefficient=1, degree_hours=self.degree_hours, thermal_conductance=1,
                                  surface_to_floor_ratio=1, internal_gain=1, satiation=1,
                                  income_per_capita=1, service_price=1)
        # self.demand_cool = demand(self.data, type = "cool")

        # diagnostics
        if run_diagnostics:
            diagnostics(self.data)

        # write outputs
        # write_outputs()

        # clean up and close
        # clean_up()