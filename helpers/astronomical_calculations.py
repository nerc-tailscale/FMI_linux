import pvlib.atmosphere

# HuHu adaptation
import config
from pvlib import location, irradiance



"""
Astronomical functions
Currently supports:
*angle of incidence(AOI)
*solar angle estimations, Apparent solar zenith and azimuth
*Air mass 

Angle of incidence is the angle between the solar panel normal angle and the angle of sunlight hitting the panel.
Solar azimuth and Zenith are the spherical coordinate angles used for describing the angle of the sun.

Both angles are useful for reflection and geometric projection functions.

Air mass 


"""




def get_solar_angle_of_incidence(dt):
    """
    Estimates solar angle of incidence at given datetime. Other parameters, tilt, azimuth and geolocation are from
    config.py.
    :param dt: Datetime object, should include date and time.
    :return: Angle of incidence in degrees. Angle between sunlight and solar panel normal
    """

    solar_azimuth, solar_apparent_zenith = get_solar_azimuth_zenit(dt)
    panel_tilt = config.tilt
    panel_azimuth = config.azimuth

    # angle of incidence, angle between direct sunlight and solar panel normal
    angle_of_incidence = irradiance.aoi(panel_tilt, panel_azimuth, solar_apparent_zenith, solar_azimuth)

    # setting upper limit of 90 degrees to avoid issues with projection functions. If light comes with an angle of 90
    # deg aoi, none should be absorbed. The same goes with angles of 90+deg
    if angle_of_incidence > 90:
        return 90

    return angle_of_incidence


def get_air_mass(time):
    """
    Generates air mass at time + solar zenith angle by using the default model
    :param time:
    :return:
    """

    solar_zenith = get_solar_azimuth_zenit(time)[1]
    air_mass = pvlib.atmosphere.get_relative_airmass(solar_zenith)
    return air_mass



def get_solar_azimuth_zenit(dt):
    """
    Returns apparent solar zenith and solar azimuth angles in degrees.
    :param dt: time to compute the solar position for.
    :return: azimuth, zenith
    """

    # panel location and installation parameters from config file
    panel_latitude = config.latitude
    panel_longitude = config.longitude

    # panel location object, required by pvlib
    panel_location = location.Location(panel_latitude, panel_longitude, tz=config.timezone)

    # solar position object
    solar_position = panel_location.get_solarposition(dt)

    # apparent zenith and azimuth, Using apparent for zenith as the atmosphere affects sun elevation.
    # apparent_zenith = Sun zenith as seen and observed from earth surface
    # zenith = True Sun zenith, would be observed if Earth had no atmosphere
    solar_apparent_zenith = solar_position["apparent_zenith"].values[0]
    solar_azimuth = solar_position["azimuth"].values[0]

    return solar_azimuth, solar_apparent_zenith


def __debug_add_solar_angles_to_df(df):
    """
    This function is here for debug purposes, adds angle values to dataframe
    """

    def helper_add_zenith(df):
        azimuth, zenith = get_solar_azimuth_zenit(df["time"])
        return zenith

    # applying helper function to dataset and storing result as a new column
    df["zenith"] = df.apply(helper_add_zenith, axis=1)


    def helper_add_azimuth(df):
        azimuth, zenith = get_solar_azimuth_zenit(df["time"])
        return azimuth

    # applying helper function to dataset and storing result as a new column
    df["azimuth"] = df.apply(helper_add_azimuth, axis=1)

    def helper_add_aoi(df):
        aoi = get_solar_angle_of_incidence(df["time"])
        return aoi

    # applying helper function to dataset and storing result as a new column
    df["aoi"] = df.apply(helper_add_aoi, axis=1)

    return df