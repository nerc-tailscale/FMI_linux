import datetime
import pandas




#############################################################################################
#### This file can be removed before open source release                                #####
#############################################################################################

def __get_data_for_days(start_date, days, file):
    """
    This function reads known production values from helsinki 2022-2023 dataset
    Returns data for start_date + n days
    """
    # reading csv
    actual_production = pandas.read_csv(file, sep=";", parse_dates=["prod_time"])

    # taking relevant parameters
    actual_production = actual_production[["prod_time", "pv_inv_out"]]

    # renaming columns
    actual_production.columns = ["time", "power"]

    # dropping na power values
    actual_production = actual_production.dropna()

    # formatting time column from text to datetime
    actual_production['time'] = pandas.to_datetime(actual_production['time'])

    # choosing relevant time interval
    actual_production = actual_production[actual_production["time"] >= start_date]
    actual_production = actual_production[actual_production["time"] <= start_date + datetime.timedelta(days=days+1) ]
    actual_production = actual_production.dropna()

    return actual_production

def get_data_for_days_kuopio(start_date, days):
    """
    This function reads known production values from Kuopio 2022-2023 dataset
    Returns data for start_date + n days
    """
    return __get_data_for_days(start_date, days, "helpers/pv_prod_Kuopio_2022-2023_vs2.csv")

def get_data_for_days_helsinki(start_date, days):
    """
    This function reads known production values from Helsinki 2022-2023 dataset
    Returns data for start_date + n days
    """
    return __get_data_for_days(start_date, days, "helpers/pv_prod_Helsinki_2022-2023.csv")


#get_data_for_days(datetime.datetime(2023, 7, 12), 2)