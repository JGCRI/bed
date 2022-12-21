"""
@Date:
@authors:
@Project: bed v0.0

License:  BSD 2-Clause, see LICENSE and DISCLAIMER files
Copyright (c) 2022, Battelle Memorial Institute

"""

import logging

class Bed:
    """ Model wrapper for bed"""

    def __init__(self):
        self.var1 = 0.125
        self.var = 5


def fake2(fake_param: int = 1):
    """Fake function to remove.

    :param fake_param:                          A fake integer
    :type fake_param:                           int

    :return:                                    boolean value

    """

    logging.info('This is a log file for fake 2')

    return True