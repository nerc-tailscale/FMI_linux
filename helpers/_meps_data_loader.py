#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 14:07:48 2023

MEPS open data collection for parameters needed in PV forecasting

@author: kalliov (Viivi Kallio)
"""
import datetime as dt
import pandas as pd
import numpy as np
from fmiopendata.wfs import download_stored_query

from helpers import astronomical_calculations

pd.set_option('display.max_rows', 500)
pd.set_option('display.min_rows', 500)


def collect_fmi_opendata(latlon, start_time, end_time):
    collection_string = "fmi::forecast::harmonie::surface::point::multipointcoverage"

    # List the wanted MEPS parameters
    parameters = ["Temperature",
                  "RadiationGlobalAccumulation",
                  "RadiationNetSurfaceSWAccumulation",
                  "RadiationSWAccumulation",
                  "WindSpeedMS",
                  "TotalCloudCover"
                  ]
    parameters_str = ','.join(parameters)

    # Collect data
    snd = download_stored_query(collection_string,
                                args=["latlon=" + latlon,
                                      "starttime=" + str(start_time),
                                      "endtime=" + str(end_time),
                                      'parameters=' + parameters_str])
    data = snd.data

    # Times to use in forming dataframe
    data_list = []
    # Make the dict of dict of dict of.. into pandas dataframe
    for time, location_data in data.items():
        location = list(location_data.keys())[0]  # Get the location dynamically
        values = location_data[location]

        data_list.append({'Time': time,
                          'T': values['Air temperature']['value'],
                          'GHI_accum': values['Global radiation accumulation']['value'],
                          'NetSW_accum': values['Net short wave radiation accumulation at the surface']['value'],
                          'DirHI_accum': values['Short wave radiation accumulation']['value'],
                          'Wind speed': values['Wind speed']['value'],
                          'Total cloud cover': values['Total cloud cover']['value']})

    # Create a DataFrame and set time as index   
    df = pd.DataFrame(data_list)
    df.set_index('Time', inplace=True)

    # Calculate instant from accumulated values (only radiation parameters)
    diff = df.diff()
    df['GHI'] = diff['GHI_accum'] / (60 * 60)
    df['NetSW'] = diff['NetSW_accum'] / (60 * 60)
    df['DirHI'] = diff['DirHI_accum'] / (60 * 60)
    # GHI = grad_instant
    # DirHI = swavr_instant
    # netSW = nswrs_instant

    # Calculate albedo (refl/ghi), refl=ghi-net
    df['albedo'] = (df['GHI'] - df['NetSW']) / df['GHI']

    # Calculate Diffuse horizontal from global and direct
    df['DHI'] = df['GHI'] - df['DirHI']
    #

    # Adding solar zenith angle to df
    def sza_adder(df_input):
        return astronomical_calculations.get_solar_azimuth_zenit(df_input["time"])[1]


    df["time"] = df.index
    df["sza"] = df.apply(sza_adder, axis=1)
    # solar zenit angle added

    # Calculate dni from dhi
    df['DNI'] = df['DirHI'] / np.cos(df['sza'] * (np.pi / 180))

    # Keep the necessary parameters
    df = df[['DNI', 'DHI', 'GHI', 'DirHI', 'albedo',
             'T', 'Wind speed', 'Total cloud cover']]

    df.columns = ["dni", "dhi", "ghi", "dir_hi", "albedo", "T", "wind", "cloud_cover"]

    df.insert(loc=0, column="time", value=df.index)

    # shifting timestamps to time-interval centers as timestamp for 12:00 refers to average during 11:00-12:00
    df["time"] = df["time"] + dt.timedelta(minutes=-30)
    # adding utc timezone marker to time
    df["time"] = df["time"].dt.tz_localize("UTC")

    # restricting values to zero
    clip_columns = ["dni", "dhi", "ghi"]
    df[clip_columns] = df[clip_columns].clip(lower=0.0)
    df.replace(-0.0, 0.0, inplace=True)

    return (df)
