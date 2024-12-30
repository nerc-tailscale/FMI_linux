"""
Config file, used for storing parameters which are installation specific and fixed. Geolocation, panel angles, timezone
and data resolution belong here. Variables in this file should be expected to stay unmodified during a simulation.
"""

##### Plotting parameters
# site name used for plotting and saved file name
site_name = "EduCity"
save_directory = "output/"

#### SIMULATED INSTALLATION PARAMETERS BELOW:
# coordinates
# 60.44847441478909, 22.297553686275748
latitude = 60.448
longitude = 22.297
elevation = 29

# FMI 
#latitude, longitude = 60.2044, 24.9625

# Educity 
latitude, longitude = 60.448, 22.297 # Use this to compare meteo data with measured data

# Tyyssija 
#latitude, longitude = 60.462, 22.288 # Use this to compare PV production simulation with real production

# TYYSSIJA CONFIGURATION
tilt = 20 # degrees. Panel flat on the roof would have tilt of 0. Wall mounted panels have tilt of 90.
azimuth = 180 # degrees, north is 0 degrees, east 90. Clockwise rotation

# rated installation power in kW, PV output at standard testing conditions
rated_power = 142 # unit kW

# ground albedo near solar panels, 0.25 is PVlib default. Has to be in range [0,1], typical values [0.1, 0.4]
# grass is 0.25, snow 0.8, worn asphalt 0.12. Values can be found from wikipedia https://en.wikipedia.org/wiki/Albedo
albedo = 0.17

# module elevation, measured from ground
module_elevation = 25 # unit meters

# dummy wind speed(meter per second) value, this will be used if wind speed from fmi open is not used
wind_speed = 2

# air temp in Celsius, this will be used if temp from fmi open is not used
air_temp = 20


#### OTHER PARAMETERS

# "Europe/Helsinki" should take summer/winter time into account, "GTM" is another useful timezone
# timezone is currently not utilized as it should due to plotting issues
timezone = "UTC"

# data resolution, how many minutes between measurements. Recommending values 30, 15, 10, 5, 1
data_resolution = 15




########### PARAMETERS FOR FMI INSTALLATIONS BELOW:
# known location specific params:
latitude_helsinki = 60.2044
longitude_helsinki = 24.9625

latitude_kuopio = 62.8919
longitude_kuopio = 27.6349


elevation_helsinki = 17
elevation_kuopio = 10

tilt_helsinki = 15
tilt_kuopio = 15

azimuth_helsinki = 135
azimuth_kuopio = 217

rated_power_kuopio = 20.28
rated_power_helsinki = 21

def set_params_helsinki():
    latitude = latitude_helsinki
    longitude = longitude_helsinki
    tilt = tilt_helsinki
    azimuth = azimuth_helsinki
    rated_power = rated_power_helsinki
    module_elevation = elevation_helsinki

def set_params_kuopio():
    latitude = latitude_kuopio
    longitude = longitude_kuopio
    tilt = tilt_kuopio
    azimuth = azimuth_kuopio
    rated_power = rated_power_kuopio
    module_elevation = elevation_kuopio

def set_params_tyyssija():
    latitude = 60.462 
    longitude = 22.288
    tilt = 20
    azimuth = 180
    rated_power = 142
    module_elevation = 25