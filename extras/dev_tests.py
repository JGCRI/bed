# ALT + SHIFT + E
# CTRL + ALT + L (Reformat)
# CTRL + / to comment out groups of lines
# In terminal for testing
# pip install pytest
# pytest
import os
import xesmf as xe
import xarray as xr
import numpy as np
import bed
# a1 = bed.Bed(config_file= os.path.join(data_folder,"example_config.yml")) # Coming from Model.py

# Get example data
data_folder = bed.get_data()

# Read Config
config = bed.read_config(config_file = os.path.join(data_folder, "example_config.yml"))

# Read Data
data = bed.Data(config_file=os.path.join(data_folder, "example_config.yml"))
data.example_dataset
data.temperature
ds = data.population
# target_resolution = 0.5
# method = 'extensive'
# regrid_ds = data.regrid(ds=data.population, target_resolution=0.5, method='extensive')

# example to use xesmf
resolution = 0.5
offset = resolution /2

ds_out = xr.Dataset({
    "lat": (["lat"], np.linspace(90 - offset, -90 + offset, 15), {"units": "degrees_north"}),
    "lon": (["lon"], np.linspace(-180 + offset, 180 - offset, 15), {"units": "degrees_east"}),
})

ds_out = xr.Dataset({
            "lat": (["lat"], np.linspace(90 - offset, -90 + offset, 180), {"units": "degrees_north"}),
            "lon": (["lon"], np.linspace(-180 + offset, 180 - offset, 360), {"units": "degrees_east"})
        })
# takes about 4 min
ds_test = ds.isel(lat=slice(0,1117), lon=slice(0,2880))
regridder = xe.Regridder(ds_test, ds_out, "conservative")

ds_out = regridder(ds_test)


# example using xesmf
import os
import xesmf as xe
import xarray as xr
import numpy as np

ds = xr.tutorial.open_dataset("air_temperature")
ds  # air temperature in Kelvin

# input dataset can contain variables of different shapes (e.g. 2D, 3D, 4D), as long as horizontal shapes are the same.
ds["celsius"] = ds["air"] - 273.15  # Kelvin -> celsius
ds["slice"] = ds["air"].isel(time=0)
ds

ds_out = xr.Dataset(
    {
        "lat": (["lat"], np.arange(16, 75, 1.0)),
        "lon": (["lon"], np.arange(200, 330, 1.5)),
    }
)

regridder = xe.Regridder(ds, ds_out, "bilinear")
regridder

# the entire dataset can be processed at once
ds_out = regridder(ds)
ds_out


# Run Diagnsotics
bed.diagnostics(data=data)

# run the entire model
import os
os.chdir('C:/WorkSpace/github/bed')
import bed

data_folder = bed.get_data()
b = bed.Bed(config_file=os.path.join(data_folder, "example_config.yml"), diagnostics=False)


# bed.get_data()
#
# # In terminal
# # pip install pytest
# # pytest
#
# # Test plotting
# Read a xarray
# import bed
# import pandas as pd
# import xarray as xr
# import matplotlib.pyplot as plt
# ds = xr.open_dataset(r'C:\Z\models\bed_data\wrfout_d03_2014-08-09_Morocco_2014.nc')
# ds
# ds.data_vars
# ds.T2.XTIME
# t2_cold = ds.T2.isel(Time=1)
# t2_hot = ds.T2.isel(Time=12)
# t2 = xr.concat([t2_cold, t2_hot], pd.Index(['Night', 'Day'], name='Cycle'))
# t2.values.shape
# t2.coords
# t2.plot(x="west_east", y="south_north", col="Cycle")
# plt.show()
