"""
@Date:
@authors:
@Project: bed v0.0

License:  BSD 2-Clause, see LICENSE and DISCLAIMER files
Copyright (c) 2022, Battelle Memorial Institute

        # Calculate building energy demand
        #   dh energy demand per unit floorspace (GJ/m2) heating
        #   dh energy demand per unit floorspace (GJ/m2) heating

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

        # heating energy demand
        # dh = kh (HDH.n.R - IG)[ 1 - exp( - (ln2/uh) . (i/Ph) ) ]

        # cooling energy demand
        # dc = kc (CDH.n.R - IG)[ 1 - exp( - (ln2/uc) . (i/Pc) )]

"""

from bed.read_config import read_config

class Bed:
    """ Model wrapper for bed"""

    def __init__(self, config_file='config'):
        self.var1 = 0.125
        self.var = 5

        # Read in Config File
        self.config = read_config(config_file)

        # Read data
        # self.data = read_data(self.config)

        # Calculate building energy demand
        # self.demand_heat = demand(self.data, type="heat")
        # self.demand_cool = demand(self.data, type = "cool")

        # diagnostics
        # diagnostics()

        # write outputs
        # write_outputs()

        # clean up and close
        # clean_up()

    def clean_up(fake_param: int = 1):
        """Fake function to remove.

        :param fake_param:                          A fake integer
        :type fake_param:                           int

        :return:                                    boolean value

        """

        return True