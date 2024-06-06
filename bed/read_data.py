import logging
import pandas as pd
import xarray as xr
import numpy as np
import os as os
import xesmf as xe
from bed.read_config import read_config

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

    def __init__(self, config_file=''):
        """
        :param config_file:         String for configuration file path
        :type config_file:          string
        :return:                    Data
        """

        logging.info('Starting class Data inside module read_data...')

        self.config = read_config(config_file=config_file)
        self.temperature_in = None
        self.population_in = None

        if self.config != '':

            # Create folders for outputs in same location as config
            self.dir_root = os.path.dirname(os.path.abspath(config_file))
            self.dir_outputs = os.path.abspath(os.path.join(self.dir_root, self.config['dir_outputs']))
            self.dir_diagnostics = os.path.abspath(os.path.join(self.dir_outputs, "diagnostics"))

            if not os.path.exists(self.dir_outputs):
                logging.info(f'Creating: {self.dir_outputs}')
                os.makedirs(self.dir_outputs, exist_ok=True)

            if not os.path.exists(self.dir_diagnostics):
                logging.info(f'Creating: {self.dir_diagnostics}')
                os.makedirs(self.dir_diagnostics, exist_ok=True)

            # Read datasets
            # Assume datasets are in same folder as config_file
            if os.path.exists(os.path.abspath(os.path.join(self.dir_root, self.config['path_example_data_set']))):
                self.example_dataset = pd.read_csv(os.path.abspath(os.path.join(self.dir_root, self.config['path_example_data_set'])))
            else: # If user gives full path
                self.example_dataset = pd.read_csv(os.path.abspath(self.config['path_example_data_set']))

            if os.path.exists(os.path.abspath(os.path.join(self.dir_root, self.config['path_temperature_ncdf']))):
                self.temperature = self.read_temperature(os.path.abspath(os.path.join(self.dir_root, self.config['path_temperature_ncdf'])))
            else: # If user gives full path
                self.temperature = self.read_temperature(self.config['path_temperature_ncdf'])

            if os.path.exists(os.path.abspath(os.path.join(self.dir_root, self.config['path_population_ncdf']))):
                self.population = self.read_population(os.path.abspath(os.path.join(self.dir_root, self.config['path_population_ncdf'])))
            else: # If user gives full path
                self.population = self.read_population(self.config['path_population_ncdf'])

            self.target_resolution = self.config['target_resolution']

        # Regrid each data
        self.temperature = self.regrid(ds=self.temperature)
        self.population = self.regrid(ds=self.population)

        logging.info('Class Data inside module read_data completed.')

    def read_temperature(self, path_temperature_ncdf, var_temperature='T2'):
        """Read WRF temperature data and reformat for regridding"""

        # open netCDF as xarray dataset
        ds = xr.open_dataset(path_temperature_ncdf)
        
        # coordinate names
        coords_name = list(ds.coords.keys())
        lat_name = [i for i in coords_name if 'lat' in i.lower()][0]
        lon_name = [i for i in coords_name if 'lon' in i.lower()][0]

        # rename south_north and west_east to lat and lon for xesmf regridder        
        if lat_name != 'lat' or lon_name != 'lon':
            ds = ds.rename({lat_name: 'lat', lon_name:'lon'})
            
        # get only temperature
        self.temperature_in = ds[var_temperature]
        
        ds_temp = self.temperature_in

        # change 3D lat and lon to 2D for xesmf regridder
        lat = ds_temp.lat.values[0,:,:]
        lon = ds_temp.lon.values[0,:,:]
        time = ds_temp.XTIME.values
        temp = ds_temp.values

        ds_out = xr.Dataset(
            {
                "temperature": ([ "time", "south_north", "west_east"], temp)
            },
            coords={
                "lon": (["south_north", "west_east"], lon),
                "lat": (["south_north", "west_east"], lat),
                "time": time
            }
        )

        return ds_out
    
    def read_population(self, path_population_ncdf):
        """Read WRF temperature data and reformat for regridding"""

        # open netCDF as xarray dataset
        ds = xr.open_dataset(path_population_ncdf)
        
        # var name
        var_name = list(ds.keys())[0]
        coords_name = list(ds.coords.keys())
        lat_name = [i for i in coords_name if 'lat' in i.lower()][0]
        lon_name = [i for i in coords_name if 'lon' in i.lower()][0]
        
        # rename south_north and west_east to lat and lon for xesmf regridder
        ds = ds.rename({var_name: 'population'})
        
        if lat_name != 'lat' or lon_name != 'lon':
            ds = ds.rename({lat_name: 'lat', lon_name:'lon'})
            
        # get only temperature
        self.population_in = ds['population']

        # change 3D lat and lon to 2D for xesmf regridder
        # lat = ds_temp.lat.values[:,:]
        # lon = ds_temp.lon.values[:,:]
        # pop = ds_temp.values

        # ds_out = xr.Dataset(
        #     {
        #         "population": ([ "south_north", "west_east"], pop)
        #     },
        #     coords={
        #         "lon": (["south_north", "west_east"], lon),
        #         "lat": (["south_north", "west_east"], lat)
        #     }
        # )

        return self.population_in

    @staticmethod
    def set_global_coords(ds, resolution):
        """Create global coordinates based on resolution

        :param resolution:      Float for resolution in degrees
        """

        lon_min = ds.lon.values.min()
        lon_max = ds.lon.values.max()
        lat_min = ds.lat.values.min()
        lat_max = ds.lat.values.max()
        
        offset = resolution / 2

        coords = xr.Dataset({
            "lat": (["lat"], np.linspace(90 - offset, -90 + offset, round(180 / resolution)), {"units": "south_north"}),
            "lon": (["lon"], np.linspace(-180 + offset, 180 - offset, round(360 / resolution)), {"units": "west_east"}),
        })
        
        # slice the coordinate to the data extent
        coords_extent = coords.where((coords.lat>=lat_min) & 
                                     (coords.lat<=lat_max) & 
                                     (coords.lon >= lon_min) & 
                                     (coords.lon <= lon_max), 
                                     drop = True)

        return coords_extent

    def regrid(self, ds, method='bilinear'):
        """Simple regridding algorithm

        :param ds:                  xarray Dataset or DataArray, needs lat and lon and global extent
        :param target_resolution:   String for target resolution in degrees
        :param method:              String for choice of 'extensive' (preserves sums, default), 'intensive' (take average), or 'label' (for maps)
        :return:                    xarray Dataset regridded to target_resolution
        """

        # Set target coordinates
        ds_out = self.set_global_coords(ds=ds, resolution=self.target_resolution)


        # Perform regridding
        regridder = xe.Regridder(ds, ds_out, method)

        # Regrid with a Data Array
        ds_out = regridder(ds)


        return ds_out

