import os
import pandas as pd
import datetime
import config      # HuHu Modification
import helpers.geometric_projections
from helpers import solar_irradiance_estimator, astronomical_calculations
from helpers import reflection_estimator
from helpers import panel_temperature_estimator
from helpers import output_estimator
from apscheduler.schedulers.blocking import BlockingScheduler


"""
Main file, shows examples on how to call the functions from other files.

Modify parameters in file config.py in order to change the simulated installation location and other installation 
parameters.

full_processing_of_fmi_open_data()
-generates solar pv forecast data with fmi open and plots a minimal plot

full_processing_of_pvlib_open_data()
-generates solar pv forecast data with pvlib and plots a minimal plot

get_fmi_data(day_range)
-generates a power generation dataframe by using fmi open

get_pvlib_data(day_range)
-generates a power generation dataframe by using pvlib

combined_processing_of_data()
-used get_fmi_data and get_pvlib_data to generate dataframes. Plots the data with plotter monoplot.
plot shows power(W) and energy(kWh) values for each day.


TODO: Current generation functions are slow. This is not a problem with the small amount of data which is required
here, but faster data generation would be beneficial for other applications.

Currently plots are not time zone aware, plots show utc time even if timestamps have +02:00 time zone marker in them.
Figure out why this happens and fix it.

"""

def print_full(x):
    """
    Prints a dataframe without leaving any columns or rows out. Useful for debugging.
    """

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1400)
    pd.set_option('display.float_format', '{:10,.2f}'.format)
    pd.set_option('display.max_colwidth', None)
    print(x)
    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')
    pd.reset_option('display.width')
    pd.reset_option('display.float_format')
    pd.reset_option('display.max_colwidth')

def full_processing_of_fmi_open_data():
    # date for simulation:
    today = datetime.date.today()
    date_start = datetime.datetime(today.year, today.month, today.day)

    # step 1. simulate irradiance components dni, dhi, ghi:
    data = solar_irradiance_estimator.get_solar_irradiance(date_start, day_count=3, model="fmiopen")

    # step 2. project irradiance components to plane of array:
    data = helpers.geometric_projections.irradiance_df_to_poa_df(data)

    # step 3. simulate how much of irradiance components is absorbed:
    data = helpers.reflection_estimator.add_reflection_corrected_poa_components_to_df(data)

    # step 4. compute sum of reflection-corrected components:
    data = helpers.reflection_estimator.add_reflection_corrected_poa_to_df(data)

    # step 5. estimate panel temperature based on wind speed, air temperature and absorbed radiation
    data = helpers.panel_temperature_estimator.add_estimated_panel_temperature(data)

    # step 6. estimate power output
    data = helpers.output_estimator.add_output_to_df(data)

    # printing and plotting data
    print_full(data)

    plotter.init_plot()
    plotter.add_label_x("Time")
    plotter.add_label_y("Output(W)")
    plotter.add_title("Simulated solar PV system output")
    plotter.plot_curve(data["time"], data["output"], label="Output(W)")
    plotter.plot_kwh_labels(data)
    plotter.show_legend()
    plotter.show_plot()

def full_processing_of_pvlib_data():


    # date for simulation:
    today = datetime.date.today()
    date_start = datetime.datetime(today.year, today.month, today.day)

    # step 1. simulate irradiance components dni, dhi, ghi:
    data = solar_irradiance_estimator.get_solar_irradiance(date_start, day_count=3, model="pvlib")

    # step 2. project irradiance components to plane of array:
    data = helpers.geometric_projections.irradiance_df_to_poa_df(data)

    # step 3. simulate how much of irradiance components is absorbed:
    data = helpers.reflection_estimator.add_reflection_corrected_poa_components_to_df(data)

    # step 4. compute sum of reflection-corrected components:
    data = helpers.reflection_estimator.add_reflection_corrected_poa_to_df(data)

    # step 4.1. add dummy wind and air temp data
    data = helpers.panel_temperature_estimator.add_dummy_wind_and_temp(data, config.wind_speed, config.air_temp)

    # step 5. estimate panel temperature based on wind speed, air temperature and absorbed radiation
    data = helpers.panel_temperature_estimator.add_estimated_panel_temperature(data)

    # step 6. estimate power output
    data = helpers.output_estimator.add_output_to_df(data)

    # printing and plotting data
    print_full(data)

    plotter.init_plot()
    plotter.add_label_x("Time")
    plotter.add_label_y("Output(W)")
    plotter.add_title("Simulated solar PV system output")
    plotter.plot_curve(data["time"], data["output"], label="Output(W)")
    plotter.plot_kwh_labels(data)
    plotter.show_legend()
    plotter.show_plot()

def get_fmi_data(day_range):
    """
    This function shows the steps used for generating power output data with fmi open. Also returns the power output.
    Note that FMI open only gives irradiance estimates for the next ~64 hours.
    :param day_range: Day count, 1 returns only this day, 3 returns this day and the 2 following days.
    :return: Power output dataframe
    """

    # using a temporary override of data resolution as fmi open operates on 60 minute data sections.
    # saving original data resolution
    original_data_resolution = config.data_resolution
    # setting temporary value for fmi data processing(this is restored back to original value later)
    config.data_resolution = 60

    # date for simulation:
    today = datetime.date.today()
    date_start = datetime.datetime(today.year, today.month, today.day)

    # step 1. simulate irradiance components dni, dhi, ghi:
    data = solar_irradiance_estimator.get_solar_irradiance(date_start, day_count=day_range, model="fmiopen")

    # step 2. project irradiance components to plane of array:
    data = helpers.geometric_projections.irradiance_df_to_poa_df(data)

    # step 3. simulate how much of irradiance components is absorbed:
    data = helpers.reflection_estimator.add_reflection_corrected_poa_components_to_df(data)

    # step 4. compute sum of reflection-corrected components:
    data = helpers.reflection_estimator.add_reflection_corrected_poa_to_df(data)

    # step 5. estimate panel temperature based on wind speed, air temperature and absorbed radiation
    data = helpers.panel_temperature_estimator.add_estimated_panel_temperature(data)

    # step 6. estimate power output
    data = helpers.output_estimator.add_output_to_df(data)

    config.data_resolution = original_data_resolution

    return data

def get_pvlib_data(day_range, data_fmi=None):
    """
    This function shows the steps used for generating power output data with pvlib. Also returns the power output.
    PVlib is fully simulated, no restrictions on day range.
    :param day_range: Day count, 1 returns only this day, 3 returns this day and the 2 following days.
    :param data_fmi: If fmi df is given here, it will be used as weather data donor df
    :return: Power output dataframe
    """
    # date for simulation:
    today = datetime.date.today()
    date_start = datetime.datetime(today.year, today.month, today.day)

    data_pvlib = solar_irradiance_estimator.get_solar_irradiance(date_start, day_count=day_range, model="pvlib")

    # step 2. project irradiance components to plane of array:
    data_pvlib = helpers.geometric_projections.irradiance_df_to_poa_df(data_pvlib)

    # step 3. simulate how much of irradiance components is absorbed:
    data_pvlib = helpers.reflection_estimator.add_reflection_corrected_poa_components_to_df(data_pvlib)

    # step 4. compute sum of reflection-corrected components:
    data_pvlib = helpers.reflection_estimator.add_reflection_corrected_poa_to_df(data_pvlib)

    # step 4.1. adding wind and air speed to dataframe
    if data_fmi is not None:
        # getting data from fmi dataframe if one was given
        data_pvlib = panel_temperature_estimator.add_wind_and_temp_to_df1_from_df2(data_pvlib, data_fmi)
    else:
        # using dummy values if no df was given
        data_pvlib = helpers.panel_temperature_estimator.add_dummy_wind_and_temp(data_pvlib, config.wind_speed, config.air_temp)

    # step 5. estimate panel temperature based on wind speed, air temperature and absorbed radiation
    data_pvlib = helpers.panel_temperature_estimator.add_estimated_panel_temperature(data_pvlib)

    # step 6. estimate power output
    data_pvlib = helpers.output_estimator.add_output_to_df(data_pvlib)

    data_pvlib = data_pvlib.dropna()

    return data_pvlib

# HuHu added days as input
def combined_processing_of_data(days):
    """
    Uses both pvlib and fmi open to compute solar irradiance for the next days (3 MAXIMUM) and plots both
    
    Returns: A data Frame
    """

    #print("Simulating clear sky and weather model based PV generation for the next x days.")
    # fetching fmi data and generating solar pv output df
    data_fmi = get_fmi_data(days)
    #print(data_fmi.columns)
    #data_fmi.to_csv('fmi_meteo.csv', sep=',')
    #print(data_fmi)
    # generating pvlib irradiance values and clear sky pv dataframe, passing fmi data to pvlib generator functions
    # for wind and air temp transfer
    data_pvlib = get_pvlib_data(3, data_fmi)
    #print(data_pvlib.columns)
    #print_full(data_pvlib)
    #plotter.plot_fmi_pvlib_mono(data_fmi, data_pvlib)
    return data_fmi

#### Debugging functions below
def __process_irradiance_data(meps_data):
    """
    Processing function for time, dni, dhi, ghi -dataframes
    Generates dataframe with output-variable
    If input does not contain T and wind values, dummies will be added
    """

    # step 2. project irradiance components to plane of array:
    data = helpers.geometric_projections.irradiance_df_to_poa_df(meps_data)

    # step 3. simulate how much of irradiance components is absorbed:
    data = helpers.reflection_estimator.add_reflection_corrected_poa_components_to_df(data)

    # step 4. compute sum of reflection-corrected components:
    data = helpers.reflection_estimator.add_reflection_corrected_poa_to_df(data)

    # step 4.1. add dummy wind and air temp data
    if "T" not in meps_data.columns or "wind" not in meps_data.columns:
        data = helpers.panel_temperature_estimator.add_dummy_wind_and_temp(data, config.wind_speed, config.air_temp)

    # step 5. estimate panel temperature based on wind speed, air temperature and absorbed radiation
    data = helpers.panel_temperature_estimator.add_estimated_panel_temperature(data)

    # step 6. estimate power output
    data = helpers.output_estimator.add_output_to_df(data)

    return data


#### Hugo Huerta last review 28.12.2024

# Prepare a TMY (format) file
# Configure the config file to run the following lines
headers = [f'Latitude (decimal degrees): {config.latitude}',
           f'Longitude (decimal degrees): {config.longitude}',
           f'Elevation (m): {config.elevation}',
            'month,year',
            '1.2024',
            '2.2024',
            '3.2024',
            '4.2024',
            '5.2024',
            '6.2024',
            '7.2024',
            '8.2024',
            '9.2024',
            '10.2024',
            '11.2024',
            '12.2024',
            'time(UTC),T2m,RH,G(h),Gb(n),Gd(h),IR(h),WS10m,WD10m,SP'
            ]

# File path where the CSV will be saved
fileName = '/Documents/solcast/FMI_linux/output/weatherPrediction_' + config.site_name + '_2024.csv'
#fileName = '/output/weatherPrediction_' + config.site_name + '_2024.csv'
path = os.getcwd()
file_path = path + fileName


if not os.path.exists(file_path):
# Create a file with empty lines (17 empty lines)
    with open(file_path, 'w') as f:
        # Write the details
        for element in headers:
            f.write(element + '\n')


# Define the function to be run at 11 PM
def scheduled_task():
    """

    Collect the meteodata with FMI API.

    """
    df = combined_processing_of_data(days=2)
    df.drop(['time', 'dir_hi', 'albedo',   
           'cloud_cover', 'dni_poa', 'dhi_poa', 'ghi_poa', 'poa', 'dni_rc',
           'dhi_rc', 'ghi_rc', 'poa_ref_cor', 'module_temp', 'output'], axis=1)

    " Add missing columns with average values from the site"
    df['RH']= 80
    df['IR(h)']= 296
    df['WD10m']= 202
    df['SP']= 101193

    # Rearrange accoriding to TMY format
    #TMY = df[['timeUTC','T','RH','ghi','dni','dhi','IR(h)','wind','WD10m','SP']]
    TMY = df[['T','RH','ghi','dni','dhi','IR(h)','wind','WD10m','SP']].iloc[-24:]
    # Append the DataFrame content to the created file
    TMY.to_csv(file_path, mode='a', header=None)

    print(f"Task is running at {datetime.datetime.now()}")

# Create an instance of the scheduler
scheduler = BlockingScheduler()

# Schedule the task to run every day at 11:00 PM
scheduler.add_job(scheduled_task, 'cron', hour = 23, minute = 30)

# Start the scheduler
if __name__ == "__main__":
    print("Scheduler is starting...")
    scheduler.start()
