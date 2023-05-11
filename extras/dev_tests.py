# ALT + SHIFT + E
# CTRL + ALT + L (Reformat)
# CTRL + / to comment out groups of lines

import bed
import os

# Get example data
data_folder = bed.get_data()
#
# a1 = bed.Bed(config_file= os.path.join(data_folder,"example_config.yml")) # Coming from Model.py
# bed.read_config(config_file= os.path.join(data_folder,"example_config.yml"))
# a1.config
# a1.degree_hours
# a1.demand_heat
# bed.diagnostics()
# bed.clean_up()
# bed.write_outputs()
# bed.demand()
# a1.demand_heat
# bed.temperature_to_degree_hours()
# a1.degree_hours
#
# bed.get_data()
#
# # In terminal
# # pip install pytest
# # pytest
#
# # Test plotting
# # Read a xarray
# import bed
# import pandas as pd
# import xarray as xr
# import matplotlib.pyplot as plt
# ds = xr.open_dataset(r'C:\Z\models\bed_data\wrfout_d03_2014-08-09_Morocco_2014.nc')
# ds
#
# ds.data_vars
#
# ds.T2.XTIME
#
# t2_cold = ds.T2.isel(Time=1)
# t2_hot = ds.T2.isel(Time=12)
#
# t2 = xr.concat([t2_cold, t2_hot], pd.Index(['Night', 'Day'], name='Cycle'))
# t2.values.shape
# t2.coords
#
# t2.plot(x="west_east", y="south_north", col="Cycle")
# plt.show()
