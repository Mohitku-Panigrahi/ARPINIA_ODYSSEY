import os
import netCDF4 as nc
import numpy as np

def create_era5_fixture(filepath):
    ds = nc.Dataset(filepath, 'w', format='NETCDF4')
    
    # Dimensions
    ds.createDimension('longitude', 3)
    ds.createDimension('latitude', 3)
    ds.createDimension('time', 3)
    
    # Variables
    lons = ds.createVariable('longitude', 'f4', ('longitude',))
    lons.units = 'degrees_east'
    lats = ds.createVariable('latitude', 'f4', ('latitude',))
    lats.units = 'degrees_north'
    times = ds.createVariable('time', 'f4', ('time',))
    times.units = 'hours since 2018-08-13 00:00:00'
    times.calendar = 'gregorian'
    
    u10 = ds.createVariable('u10', 'f4', ('time', 'latitude', 'longitude'), fill_value=-32767.0)
    u10.units = 'm s**-1'
    u10.long_name = '10 metre U wind component'
    
    v10 = ds.createVariable('v10', 'f4', ('time', 'latitude', 'longitude'), fill_value=-32767.0)
    v10.units = 'm s**-1'
    v10.long_name = '10 metre V wind component'
    
    # Data: 33.1 to 33.8 lon, 33.7 to 33.2 lat (descending like typical ERA5)
    lons[:] = [33.1, 33.5, 33.9]
    lats[:] = [33.7, 33.4, 33.1]
    times[:] = [15, 16, 17] # 15:00 to 17:00 on Aug 13
    
    # Known uniform field for testing: u10=5.0, v10=-2.0
    u10[:] = np.full((3, 3, 3), 5.0)
    v10[:] = np.full((3, 3, 3), -2.0)
    
    ds.close()

def create_cmems_fixture(filepath):
    ds = nc.Dataset(filepath, 'w', format='NETCDF4')
    
    # Dimensions
    ds.createDimension('longitude', 3)
    ds.createDimension('latitude', 3)
    ds.createDimension('time', 3)
    ds.createDimension('depth', 2)
    
    # Variables
    lons = ds.createVariable('longitude', 'f4', ('longitude',))
    lons.units = 'degrees_east'
    lats = ds.createVariable('latitude', 'f4', ('latitude',))
    lats.units = 'degrees_north'
    times = ds.createVariable('time', 'f4', ('time',))
    times.units = 'hours since 2018-08-13 00:00:00'
    times.calendar = 'standard'
    depth = ds.createVariable('depth', 'f4', ('depth',))
    depth.units = 'm'
    
    uo = ds.createVariable('uo', 'f4', ('time', 'depth', 'latitude', 'longitude'), fill_value=-32767.0)
    uo.units = 'm s-1'
    
    vo = ds.createVariable('vo', 'f4', ('time', 'depth', 'latitude', 'longitude'), fill_value=-32767.0)
    vo.units = 'm s-1'
    
    # Data: ascending lat for CMEMS
    lons[:] = [33.1, 33.5, 33.9]
    lats[:] = [33.1, 33.4, 33.7]
    times[:] = [15, 16, 17] 
    depth[:] = [0.49, 1.5] # ~Surface and next level
    
    # Known uniform field: uo=0.5, vo=0.1
    uo[:] = np.full((3, 2, 3, 3), 0.5)
    vo[:] = np.full((3, 2, 3, 3), 0.1)
    
    ds.close()

if __name__ == '__main__':
    create_era5_fixture('tests/fixtures/era5_fixture.nc')
    create_cmems_fixture('tests/fixtures/cmems_fixture.nc')
    print("Fixtures created successfully.")
