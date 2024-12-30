import numpy
import pandas
import datetime as dt
from datetime import timedelta
from helpers import astronomical_calculations


def print_full(x):
    """
    Prints a dataframe without leaving any columns or rows out. Useful for debugging.
    """

    pandas.set_option('display.max_rows', None)
    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.width', 1400)
    pandas.set_option('display.float_format', '{:10,.2f}'.format)
    pandas.set_option('display.max_colwidth', None)
    print(x)
    pandas.reset_option('display.max_rows')
    pandas.reset_option('display.max_columns')
    pandas.reset_option('display.width')
    pandas.reset_option('display.float_format')
    pandas.reset_option('display.max_colwidth')


def meps_rad_to_ghi_dni_dhi(meps_data):
    """
    This function formats meps dataframes further, removing somewhat cryptic swarv_instant -like variables.
    And adding ghi, dhi, dni which are required for unified processing

    formatting meps data, starting with:
                     date  grad_instant  swavr_instant  nswrs_instant          t          u          v       wind
    97150 2023-07-13 02:00:00           NaN            NaN            NaN      15.36       0.51      -3.04       0.00
    97151 2023-07-13 03:00:00           NaN            NaN          58.92      16.62      -0.49      -2.74       0.00
    97152 2023-07-13 04:00:00        163.00          97.44         146.38      18.46      -0.26      -2.39       0.00
    97153 2023-07-13 05:00:00        283.83         198.76         255.67      20.38       0.75       0.06       0.90
    97154 2023-07-13 06:00:00        412.47         311.48         372.52      21.20       0.80       1.40       1.48
    97155 2023-07-13 07:00:00        535.91         420.91         483.94      21.56       0.25       4.21       2.11
    97156 2023-07-13 08:00:00        638.23         154.42         576.11      22.07       0.62       2.92       1.88
    97157 2023-07-13 09:00:00        721.49         464.92         651.21      23.59      -0.14       2.88       1.65
    """

    # renaming variables to match code by @viivik
    df = meps_data.copy()
    df["ghi"] = df["grad_instant"]  # OK
    df["net_sw"] = df["nswrs_instant"]  # OK
    df["dir_hi"] = df["swavr_instant"]  # OK

    # translating variables to albedo, dhi, ghi using equations from _meps_data_loader.py
    df['albedo'] = (df['ghi'] - df['net_sw']) / df['ghi']
    df['dhi'] = df['ghi'] - df['dir_hi']

    # shifting time by 30 minutes as datapoints are hourly and they represent the average of last hour.
    df["date"] = df["date"] + dt.timedelta(minutes=-30)

    # adding apparent solar zenit angle with shifted time
    def sza_adder(df_input):
        return astronomical_calculations.get_solar_azimuth_zenit(df_input["date"])[1]

    df["sza"] = df.apply(sza_adder, axis=1)

    # shifting time back by 30 minutes, restoring original times
    df["date"] = df["date"] + dt.timedelta(minutes=30)

    # Calculate dni from dhi
    df['dni'] = df['dir_hi'] / numpy.cos(df['sza'] * (numpy.pi / 180))

    # saving only relevant parameters to output df
    df = df[["date", "ghi", "dni", "dhi"]]
    df.columns = ["time", "ghi", "dni", "dhi"]
    df["T"] = meps_data["t"]
    df["wind"] = meps_data["wind"]
    df.index = df["time"]

    # debug plotting
    # matplotlib.pyplot.plot(df["time"], df["dni"])
    # matplotlib.pyplot.plot(df["time"], df["dhi"])
    # matplotlib.pyplot.plot(df["time"], df["ghi"])
    # matplotlib.pyplot.show()

    return df

